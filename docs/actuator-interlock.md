# Physical actuator interlock

## Purpose

The pendulum FSM and the physical actuator layer intentionally enforce route
switching safety independently.

The FSM provides STARTUP_DEADTIME / DEADTIME_TO_A / DEADTIME_TO_B.

The actuator interlock additionally refuses to release any physical fan target
until the commanded mechanical route has remained unchanged for:

measured servo travel time + configured settling margin

This means an accidentally short FSM dead-time does not automatically become a
fan-versus-moving-damper hazard.

## Pipeline

logical controller output
  -> TTL / sequence validation
  -> logical-role -> fan-bank mapping
  -> dual-T-diverter route target
  -> independent servo movement timer
  -> physical fan release only after route stable

## Fail-safe default

config/defaults.json deliberately contains servo_travel_ms = null and
servo_settle_ms = 500.

A null travel time means uncalibrated.

In that state the adapter:

- may expose the desired route command,
- keeps fan_1/fan_2/fan_3 at 0 percent,
- reports SERVO_TIMING_UNCALIBRATED,
- never guesses an MZ966 travel time.

After the real dual-diverter mechanism is measured, servo_travel_ms must be set
from the worst loaded A->B / B->A travel measurement. The settling margin is a
separate engineering allowance.

## Route state

The adapter tracks:

- commanded_route
- stable_route
- route_started_at_ms
- last_sequence
- last_command_id

If the desired route differs from the stable route, all physical fans remain
off until the calibrated movement+settle window has elapsed.

The V0.3 mechanical units are supply_t_diverter and exhaust_t_diverter, with
mechanism coupled_dual_t_diverter and coupling single_servo_linkage.

## Command validation

The adapter rejects/fails safe on:

- missing command
- invalid sequence
- invalid command ID
- invalid generated/expiry timestamps
- expiry before generation
- expired command
- sequence regression
- invalid hardware map
- actuator adapter exceptions

Expired/rejected commands produce zero physical fan targets.

## Reconnect behavior

Node-RED actuator state starts with no known stable route.

Therefore after process restart/redeploy:

1. desired route is commanded,
2. all fans remain OFF,
3. the route must complete a full calibrated travel + settle interval,
4. only then can active fan targets be released.

No remembered/non-zero fan state is trusted across restart.

## Node-RED

Use:

duepoint-control -> duepoint-actuator -> WLED/GPIO protocol adapter

duepoint-actuator is responsible for command TTL, sequence-regression
protection, physical fan mapping, route movement timing and fan-off interlock.

The final WLED/GPIO protocol adapter remains hardware-specific and must still
be bench-validated for P12 PWM electrical behavior, shared supply-bank PWM
load, fan_3 independent PWM, MZ966 signal pin and boot/reset behavior.

Do not bypass duepoint-actuator with direct logical fan-target publications in
production.
