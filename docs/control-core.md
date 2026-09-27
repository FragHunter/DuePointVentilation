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

## Three physical fans on one GL-C-211WL

The current hardware inventory contains one GL-C-211WL and three physical P12 fans.

The logical pendulum controller still exposes four directional roles:
- room A supply
- room A exhaust
- room B supply
- room B exhaust

A separate hardware-map layer now validates the mapping from those logical roles to the three physical fan channels.

Important behavior:
- production configuration is intentionally invalid until every logical role is explicitly mapped,
- sharing one physical fan between logical roles requires explicit mechanical acknowledgement,
- if two logical roles ever command the same shared fan simultaneously, the mapper throws instead of guessing,
- the unresolved mapping is tracked in Issue #14.

The control FSM remains hardware-independent.
