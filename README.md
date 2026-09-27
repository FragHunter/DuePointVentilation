# DuePointVentilation

Open-source dew-point / moisture-controlled ventilation system with active cross ventilation.

## Project goal

Each installation consists of two independently controllable fans:

- **intake fan**: pulls outside air into the room
- **exhaust fan**: pushes room air outside

The system is orchestrated by **Node-RED**. Fan control is performed through **GLEDOPTO WLED PWM controllers**. Indoor/outdoor environmental measurements are provided by **Zigbee temperature/humidity sensors**, initially the **Aqara Temperature and Humidity Sensor T1**.

The project starts with dew-point / absolute-humidity ventilation and is intended to grow into a more capable ventilation controller with monitoring, multiple installations, adaptive fan speed and later motorized air flaps using **Miuzei 180° servos**.

## High-level architecture

```text
Aqara T1 sensor(s)
        │ Zigbee 3.0
        ▼
Zigbee coordinator
        │
        ▼
Zigbee2MQTT
        │ MQTT
        ▼
Node-RED
 ├─ sensor validation
 ├─ dew point / absolute humidity calculation
 ├─ ventilation state machine
 ├─ safety / hysteresis / timeouts
 ├─ fan speed control
 └─ monitoring / logging
        │
        ▼
WLED / GLEDOPTO PWM controller
   ├─ intake fan
   └─ exhaust fan

Future:
Node-RED → servo controller → intake/exhaust dampers
```

## Primary hardware

- 2 × PWM fans per installation
- GLEDOPTO WLED PWM controller
- Aqara Temperature and Humidity Sensor T1 (Zigbee)
- Zigbee coordinator
- Node-RED host
- MQTT broker
- optional InfluxDB + Grafana
- future: Miuzei 180° servos and motorized dampers

## Design principles

1. Node-RED is the orchestration layer.
2. MQTT is the internal device/event bus.
3. Sensor, control logic and actuator adapters remain separated.
4. Automatic ventilation fails safe if required sensor data becomes stale or invalid.
5. Intake and exhaust are modeled independently even when normally controlled as a pair.
6. Hardware-specific details remain behind adapters so the control algorithm is not tied to one WLED controller or Zigbee implementation.
7. All thresholds, hysteresis values, runtimes and calibration values are configurable.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## Status

Initial architecture and hardware integration planning.
