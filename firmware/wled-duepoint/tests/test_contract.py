from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT / "usermod_duepoint.cpp").read_text(encoding="utf-8")

def test_fan_pwm_is_exactly_25khz_and_linear_8bit():
    assert "FAN_PWM_HZ = 25000" in SRC
    assert "FAN_PWM_BITS = 8" in SRC
    assert "percentToDuty" in SRC

def test_servo_uses_independent_50hz_channel():
    assert "SERVO_PWM_HZ = 50" in SRC
    assert "SERVO_PWM_BITS = 16" in SRC
    assert "PinManager::allocateLedc(2)" in SRC
    assert "PinManager::allocateLedc(1)" in SRC

def test_fans_default_off_after_pwm_setup():
    start = SRC.index("bool initPwm()")
    end = SRC.index("char parseRoute", start)
    assert "allFansOff();" in SRC[start:end]
def test_watchdog_and_sequence_regression_exist():
    assert "DEFAULT_COMMAND_TIMEOUT_MS" in SRC
    assert "sequenceBefore" in SRC
    assert "failSafe(true)" in SRC

def test_unarmed_and_uncalibrated_states_fail_safe():
    assert "REJECT_NOT_ARMED" in SRC
    assert "REJECT_SERVO_UNCALIBRATED" in SRC
    assert "_armed = false" in SRC
    assert "_routeAUs = DEFAULT_ROUTE_A_US" in SRC
    assert "_routeBUs = DEFAULT_ROUTE_B_US" in SRC

def test_requires_dedicated_pin_owner_patch():
    assert "PinOwner::UM_DuePointActuator" in SRC
    assert "USERMOD_ID_DUEPOINT_ACTUATOR" in SRC
