# DuePoint WLED actuator usermod

Target: GL-C-211WL / classic ESP32 running a custom WLED build.

This usermod is the final protocol layer after Node-RED duepoint-actuator.
It does not repeat psychrometric or pendulum decisions.

## Outputs

- SUPPLY_PWM: linear 25 kHz / 8-bit duty for fan_1 + fan_2 shared PWM interface
- EXHAUST_PWM: linear 25 kHz / 8-bit duty for fan_3
- SERVO_PWM: independent 50 Hz / 16-bit RC-servo pulse output

GPIO numbers are runtime configuration and default to -1.

## Safety defaults

- enabled=true but armed=false
- all pins default to -1
- route A/B/safe pulses default to 1500 us, so the servo is uncalibrated
- fan PWM is forced to 0 immediately after LEDC setup
- external fail-safe interface is designed so GPIO LOW = fan PWM LOW/OFF
- local watchdog defaults to 6000 ms
- sequence regression is rejected
- invalid route, pin setup, disarmed state or uncalibrated servo keeps both fan outputs at 0

The upstream Node-RED actuator interlock still owns measured servo travel + settle timing.
The WLED watchdog is an independent communication failsafe.

## JSON command

POST to /json/state with an object named duepoint containing:

- sequence
- supply_pct
- exhaust_pct
- route

Accepted routes:

- ROOM_A_SUPPLY_ROOM_B_EXHAUST or A
- ROOM_B_SUPPLY_ROOM_A_EXHAUST or B
- SAFE or S

The same sequence number may be repeated as a heartbeat. Lower sequence numbers are rejected.
Node-RED must send a heartbeat faster than the configured WLED watchdog; recommended <= 2 s for the default 6 s timeout.

## Pin ownership patch

Current WLED out-of-tree usermods cannot define a new PinOwner without a small core patch.
This project carries a version-bounded patch adding:

- USERMOD_ID_DUEPOINT_ACTUATOR = 59
- PinOwner::UM_DuePointActuator

Do not silently switch to UM_Unspecified; pin conflict detection is part of the safety design.

Validated WLED target:

- repository: wled/WLED
- commit: 961961fdde8c22150a0212243621ee71bc9a7639
- commit date: 2026-09-25

## Build validation

Use validate_against_wled.sh with a clean disposable WLED checkout and a PlatformIO executable.
The script verifies the exact WLED base commit, applies the PinOwner patch, links this usermod and builds a classic ESP32 image.

## Bench gates before arming

- identify actual safe raw GPIO/pads on GL-C-211WL
- verify 25 kHz waveform on both fan groups
- verify external sink LOW < 0.8 V
- verify fan_1 + fan_2 shared PWM
- keep tach outputs separate
- calibrate MZ966 route A/B/safe pulses
- measure MZ966 loaded travel/current
- set Node-RED servo_travel_ms from measured worst case
- verify reset/power-cycle/Wi-Fi reconnect leaves fan PWM LOW/OFF
