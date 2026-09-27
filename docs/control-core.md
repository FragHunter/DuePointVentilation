# Control core

The first software implementation separates deterministic control logic from Node-RED wiring.

## Pipeline

Aqara T1 / Zigbee2MQTT → normalization → psychrometrics + validation → ventilation eligibility → paired pendulum state machine → logical fan targets → WLED/GLEDOPTO adapter.

The pure JavaScript modules under `src/control/` are unit-tested with Node's built-in test runner. Node-RED will act as the orchestration/wiring layer around this logic.

## Reason codes

Current ventilation decisions expose explicit reasons:

- `OUTSIDE_AIR_DRIER`
- `INSUFFICIENT_DRYING_POTENTIAL`
- `INDOOR_SENSOR_INVALID`
- `OUTDOOR_SENSOR_INVALID`
- `INDOOR_SENSOR_STALE`
- `OUTDOOR_SENSOR_STALE`
- `OUTDOOR_TEMPERATURE_LOCKOUT`

## Pendulum states

- `OFF`
- `PHASE_A`
- `DEADTIME_TO_B`
- `PHASE_B`
- `DEADTIME_TO_A`
- `FAULT`

During dead-time and fault states, both room modules receive zero fan demand.

The initial nominal timing is 60 s phase time with 3 s dead-time. Both remain configuration values and must be tuned from the heat-recovery measurement rig.

## Restart and direction-change safety

Automatic operation now enters STARTUP_DEADTIME before the first active phase after OFF or FAULT. The same all-off dead-time principle is used between PHASE_A and PHASE_B.

Each transition increments a sequence counter. Actuator output carries a validity deadline so stale commands can be rejected after MQTT/WLED reconnects.

## Direction calibration

Per-room/per-direction calibration factors allow later airflow balancing from measured bench data. This avoids assuming that identical PWM values produce identical flow through different fans/modules.
