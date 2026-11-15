#include "wled.h"

#ifndef ARDUINO_ARCH_ESP32
#error DuePointActuator requires ESP32 LEDC hardware.
#endif

#ifndef USERMOD_ID_DUEPOINT_ACTUATOR
#error Apply the DuePoint WLED PinOwner patch before compiling this usermod.
#endif

namespace {
constexpr uint32_t FAN_PWM_HZ = 25000;
constexpr uint8_t FAN_PWM_BITS = 8;
constexpr uint16_t FAN_PWM_MAX = (1U << FAN_PWM_BITS) - 1U;
constexpr uint32_t SERVO_PWM_HZ = 50;
constexpr uint8_t SERVO_PWM_BITS = 16;
constexpr uint32_t SERVO_PWM_MAX = (1UL << SERVO_PWM_BITS) - 1UL;
constexpr uint32_t SERVO_PERIOD_US = 1000000UL / SERVO_PWM_HZ;
constexpr uint32_t DEFAULT_COMMAND_TIMEOUT_MS = 6000;
constexpr uint16_t DEFAULT_SAFE_US = 1500;
constexpr uint16_t DEFAULT_ROUTE_A_US = 1500;
constexpr uint16_t DEFAULT_ROUTE_B_US = 1500;

constexpr uint8_t REJECT_NONE = 0;
constexpr uint8_t REJECT_NOT_ARMED = 1;
constexpr uint8_t REJECT_BAD_SEQUENCE = 2;
constexpr uint8_t REJECT_BAD_ROUTE = 3;
constexpr uint8_t REJECT_SERVO_UNCALIBRATED = 4;
constexpr uint8_t REJECT_PIN_SETUP = 5;

static const char UM_NAME[] PROGMEM = "DuePointActuator";
static const char UM_STATE[] PROGMEM = "duepoint";

uint8_t percentToDuty(uint8_t percent) {
  if (percent >= 100) return FAN_PWM_MAX;
  return static_cast<uint8_t>((static_cast<uint16_t>(percent) * FAN_PWM_MAX + 50U) / 100U);
}

uint32_t microsToServoDuty(uint16_t pulseUs) {
  const uint32_t bounded = constrain(static_cast<uint32_t>(pulseUs), 500UL, 2500UL);
  return (bounded * SERVO_PWM_MAX + (SERVO_PERIOD_US / 2U)) / SERVO_PERIOD_US;
}

bool sequenceBefore(uint32_t candidate, uint32_t current) {
  return static_cast<int32_t>(candidate - current) < 0;
}
}

class DuePointActuatorUsermod : public Usermod {
 private:
  bool _enabled = true;
  bool _armed = false;
  bool _pinsReady = false;
  bool _fanPwmReady = false;
  bool _servoPwmReady = false;
  int8_t _supplyPin = -1;
  int8_t _exhaustPin = -1;
  int8_t _servoPin = -1;
  uint8_t _fanLedcStart = 255;
  uint8_t _servoLedc = 255;
  uint16_t _safeUs = DEFAULT_SAFE_US;
  uint16_t _routeAUs = DEFAULT_ROUTE_A_US;
  uint16_t _routeBUs = DEFAULT_ROUTE_B_US;
  uint32_t _commandTimeoutMs = DEFAULT_COMMAND_TIMEOUT_MS;
  uint8_t _supplyPct = 0;
  uint8_t _exhaustPct = 0;
  uint32_t _lastSequence = 0;
  bool _haveSequence = false;
  uint32_t _lastCommandAt = 0;
  uint8_t _lastReject = REJECT_NONE;
  char _route = 'S';

  bool servoCalibrated() const {
    return _servoPin >= 0 && _routeAUs >= 500 && _routeAUs <= 2500 &&
           _routeBUs >= 500 && _routeBUs <= 2500 && _safeUs >= 500 &&
           _safeUs <= 2500 && _routeAUs != _routeBUs;
  }

  bool allocatePins() {
    if (_supplyPin < 0 || _exhaustPin < 0 || _servoPin < 0) return false;
    if (_supplyPin == _exhaustPin || _supplyPin == _servoPin || _exhaustPin == _servoPin) return false;
    managed_pin_type pins[] = {{_supplyPin, true}, {_exhaustPin, true}, {_servoPin, true}};
    return PinManager::allocateMultiplePins(pins, 3, PinOwner::UM_DuePointActuator);
  }

  void deallocatePins() {
    if (!_pinsReady) return;
    managed_pin_type pins[] = {{_supplyPin, true}, {_exhaustPin, true}, {_servoPin, true}};
    PinManager::deallocateMultiplePins(pins, 3, PinOwner::UM_DuePointActuator);
    _pinsReady = false;
  }

  void writeFans(uint8_t supplyPct, uint8_t exhaustPct) {
    _supplyPct = min<uint8_t>(100, supplyPct);
    _exhaustPct = min<uint8_t>(100, exhaustPct);
    if (!_fanPwmReady) return;
    ledcWrite(_fanLedcStart, percentToDuty(_supplyPct));
    ledcWrite(_fanLedcStart + 1, percentToDuty(_exhaustPct));
  }

  void allFansOff() { writeFans(0, 0); }

  void writeServoPulse(uint16_t pulseUs) {
    if (_servoPwmReady) ledcWrite(_servoLedc, microsToServoDuty(pulseUs));
  }

  void writeRoute(char route) {
    if (!servoCalibrated() || !_servoPwmReady) { _lastReject = REJECT_SERVO_UNCALIBRATED; return; }
    switch (route) {
      case 'A': writeServoPulse(_routeAUs); _route = 'A'; break;
      case 'B': writeServoPulse(_routeBUs); _route = 'B'; break;
      case 'S': writeServoPulse(_safeUs); _route = 'S'; break;
      default: _lastReject = REJECT_BAD_ROUTE; break;
    }
  }

  void failSafe(bool moveSafe) {
    allFansOff();
    if (moveSafe && _armed && servoCalibrated()) writeRoute('S');
  }

  bool initPwm() {
    _fanLedcStart = PinManager::allocateLedc(2);
    if (_fanLedcStart == 255) return false;
    _servoLedc = PinManager::allocateLedc(1);
    if (_servoLedc == 255) {
      PinManager::deallocateLedc(_fanLedcStart, 2);
      _fanLedcStart = 255;
      return false;
    }
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
    if (!ledcAttachChannel(_supplyPin, FAN_PWM_HZ, FAN_PWM_BITS, _fanLedcStart) ||
        !ledcAttachChannel(_exhaustPin, FAN_PWM_HZ, FAN_PWM_BITS, _fanLedcStart + 1) ||
        !ledcAttachChannel(_servoPin, SERVO_PWM_HZ, SERVO_PWM_BITS, _servoLedc)) {
      PinManager::deallocateLedc(_fanLedcStart, 2);
      PinManager::deallocateLedc(_servoLedc, 1);
      _fanLedcStart = 255;
      _servoLedc = 255;
      return false;
    }
#else
    ledcSetup(_fanLedcStart, FAN_PWM_HZ, FAN_PWM_BITS);
    ledcSetup(_fanLedcStart + 1, FAN_PWM_HZ, FAN_PWM_BITS);
    ledcAttachPin(_supplyPin, _fanLedcStart);
    ledcAttachPin(_exhaustPin, _fanLedcStart + 1);
    ledcSetup(_servoLedc, SERVO_PWM_HZ, SERVO_PWM_BITS);
    ledcAttachPin(_servoPin, _servoLedc);
#endif
    _fanPwmReady = true;
    _servoPwmReady = true;
    allFansOff();
    if (_armed && servoCalibrated()) writeRoute('S');
    return true;
  }

  char parseRoute(const char* route) const {
    if (route == nullptr) return 0;
    if (!strcmp(route, "ROOM_A_SUPPLY_ROOM_B_EXHAUST") || !strcmp(route, "A")) return 'A';
    if (!strcmp(route, "ROOM_B_SUPPLY_ROOM_A_EXHAUST") || !strcmp(route, "B")) return 'B';
    if (!strcmp(route, "SAFE") || !strcmp(route, "S")) return 'S';
    return 0;
  }

  bool applyCommand(JsonObject cmd) {
    if (!_enabled || !_pinsReady || !_fanPwmReady) { _lastReject = REJECT_PIN_SETUP; failSafe(false); return false; }
    if (!_armed) { _lastReject = REJECT_NOT_ARMED; failSafe(false); return false; }
    uint32_t sequence = 0;
    if (!getJsonValue(cmd[F("sequence")], sequence)) { _lastReject = REJECT_BAD_SEQUENCE; failSafe(false); return false; }
    if (_haveSequence && sequenceBefore(sequence, _lastSequence)) { _lastReject = REJECT_BAD_SEQUENCE; failSafe(false); return false; }
    const char* routeText = cmd[F("route")] | static_cast<const char*>(nullptr);
    const char route = parseRoute(routeText);
    if (!route) { _lastReject = REJECT_BAD_ROUTE; failSafe(false); return false; }
    if (route != 'S' && !servoCalibrated()) { _lastReject = REJECT_SERVO_UNCALIBRATED; failSafe(false); return false; }
    uint8_t supplyPct = 0, exhaustPct = 0;
    getJsonValue(cmd[F("supply_pct")], supplyPct);
    getJsonValue(cmd[F("exhaust_pct")], exhaustPct);
    supplyPct = min<uint8_t>(100, supplyPct);
    exhaustPct = min<uint8_t>(100, exhaustPct);
    _lastReject = REJECT_NONE;
    writeRoute(route);
    if (_lastReject != REJECT_NONE) { failSafe(false); return false; }
    writeFans(supplyPct, exhaustPct);
    _lastSequence = sequence;
    _haveSequence = true;
    _lastCommandAt = millis();
    return true;
  }

 public:
  void setup() override {
    if (!_enabled) return;
    if (!allocatePins()) { _lastReject = REJECT_PIN_SETUP; return; }
    _pinsReady = true;
    if (!initPwm()) { _lastReject = REJECT_PIN_SETUP; failSafe(false); deallocatePins(); return; }
  }

  void loop() override {
    if (!_enabled || !_pinsReady || !_armed || !_haveSequence) return;
    if ((uint32_t)(millis() - _lastCommandAt) > _commandTimeoutMs) {
      failSafe(true);
      _haveSequence = false;
    }
  }

  void addToJsonState(JsonObject& root) override {
    JsonObject state = root.createNestedObject(FPSTR(UM_STATE));
    state[F("armed")] = _armed;
    state[F("pins_ready")] = _pinsReady;
    state[F("servo_calibrated")] = servoCalibrated();
    state[F("supply_pct")] = _supplyPct;
    state[F("exhaust_pct")] = _exhaustPct;
    state[F("sequence")] = _haveSequence ? _lastSequence : 0;
    state[F("last_reject")] = _lastReject;
    char route[2] = {_route, '\0'};
    state[F("route")] = route;
  }

  void readFromJsonState(JsonObject& root) override {
    JsonObject cmd = root[FPSTR(UM_STATE)];
    if (!cmd.isNull()) applyCommand(cmd);
  }

  void addToJsonInfo(JsonObject& root) override {
    JsonObject user = root[F("u")];
    if (user.isNull()) user = root.createNestedObject(F("u"));
    JsonArray status = user.createNestedArray(F("DuePoint"));
    if (!_enabled) status.add(F("disabled"));
    else if (!_pinsReady) status.add(F("pin setup failed"));
    else if (!_armed) status.add(F("disarmed"));
    else if (!servoCalibrated()) status.add(F("servo uncalibrated"));
    else status.add(F("armed"));
  }

  void addToConfig(JsonObject& root) override {
    JsonObject top = root.createNestedObject(FPSTR(UM_NAME));
    top[F("enabled")] = _enabled;
    top[F("armed")] = _armed;
    top[F("supply_pin")] = _supplyPin;
    top[F("exhaust_pin")] = _exhaustPin;
    top[F("servo_pin")] = _servoPin;
    top[F("command_timeout_ms")] = _commandTimeoutMs;
    top[F("safe_us")] = _safeUs;
    top[F("route_a_us")] = _routeAUs;
    top[F("route_b_us")] = _routeBUs;
  }

  bool readFromConfig(JsonObject& root) override {
    JsonObject top = root[FPSTR(UM_NAME)];
    if (top.isNull()) return false;
    bool complete = true;
    complete &= getJsonValue(top[F("enabled")], _enabled);
    complete &= getJsonValue(top[F("armed")], _armed);
    complete &= getJsonValue(top[F("supply_pin")], _supplyPin);
    complete &= getJsonValue(top[F("exhaust_pin")], _exhaustPin);
    complete &= getJsonValue(top[F("servo_pin")], _servoPin);
    complete &= getJsonValue(top[F("command_timeout_ms")], _commandTimeoutMs);
    complete &= getJsonValue(top[F("safe_us")], _safeUs);
    complete &= getJsonValue(top[F("route_a_us")], _routeAUs);
    complete &= getJsonValue(top[F("route_b_us")], _routeBUs);
    _commandTimeoutMs = constrain(_commandTimeoutMs, 500UL, 60000UL);
    _safeUs = constrain(_safeUs, static_cast<uint16_t>(500), static_cast<uint16_t>(2500));
    _routeAUs = constrain(_routeAUs, static_cast<uint16_t>(500), static_cast<uint16_t>(2500));
    _routeBUs = constrain(_routeBUs, static_cast<uint16_t>(500), static_cast<uint16_t>(2500));
    return complete;
  }

  uint16_t getId() override { return USERMOD_ID_DUEPOINT_ACTUATOR; }
};

DuePointActuatorUsermod duepointActuatorUsermod;
REGISTER_USERMOD(duepointActuatorUsermod);
