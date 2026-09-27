# Control core

The first software implementation separates deterministic control logic from Node-RED wiring.

## Pipeline

Aqara T1 / Zigbee2MQTT → normalization → psychrometrics + validation → ventilation eligibility → paired pendulum state machine → logical fan targets → hardware mapping → WLED/GLEDOPTO + servo adapter.

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
- `STARTUP_DEADTIME`
- `PHASE_A`
- `DEADTIME_TO_B`
- `PHASE_B`
- `DEADTIME_TO_A`
- `FAULT`

During dead-time and fault states, both room modules receive zero fan demand.

The initial nominal timing is 60 s phase time with 3 s dead-time. Both remain configuration values and must be tuned from the heat-recovery measurement rig.

## Restart and direction-change safety

Automatic operation enters STARTUP_DEADTIME before the first active phase after OFF or FAULT. The same all-off dead-time principle is used between PHASE_A and PHASE_B.

Each transition increments a sequence counter. Actuator output carries a validity deadline so stale commands can be rejected after MQTT/WLED reconnects.

For the servo-routed topology the dead-time is also the mechanical switching window. The adapter must keep the fans off while the route servo is moving. Production dead-time must therefore be at least the measured servo travel time plus settling margin, or later be replaced by positive position feedback.

## Direction calibration

Per-room/per-direction calibration factors remain available for airflow balancing.

With the selected 2+1 topology these factors become especially important because two physical fans form the supply bank while one physical fan forms the exhaust bank. The control core may command different PWM demand for supply and exhaust in each phase.

## Three physical fans with servo routing

The selected topology is `servo_routed_2plus1`.

Physical fan grouping:

- `fan_1` + `fan_2`: parallel **supply bank**
- `fan_3`: **exhaust bank**

The fans are not reversed electrically. ROUTING-V0.3 uses two physically separate full-area T-diverters: one supply diverter and one exhaust diverter. One logical MZ966 actuator may move both shafts through a mechanical linkage, changing which room is connected to each fixed-direction fan bank.

### PHASE_A

- supply bank → room A
- room B → exhaust bank
- logical roles: room A supply + room B exhaust

### PHASE_B

- supply bank → room B
- room A → exhaust bank
- logical roles: room B supply + room A exhaust

### Dead-time routing

- `STARTUP_DEADTIME`: fans OFF, pre-position for PHASE_A
- `DEADTIME_TO_B`: fans OFF, move/pre-position for PHASE_B
- `DEADTIME_TO_A`: fans OFF, move/pre-position for PHASE_A
- `OFF` / `FAULT`: fans OFF, route to configured safe position

The hardware map rejects:

- missing or overlapping fan-group membership,
- missing servo positions,
- a route configuration that does not require fan-off while moving,
- active logical targets that contradict the selected phase/damper position.

## Electrical note on PWM parallelization

The 12 V fan supply is common/parallel.

Only fan_1 and fan_2 are candidates for a shared PWM signal because they are members of the same supply bank and always receive the same logical target in this topology.

Do not hard-wire the PWM pins together until the bench test confirms that the chosen open-drain stage can sink the combined pull-up current of both P12 PWM inputs and that boot/off behavior remains safe.

fan_3 remains a separate PWM group so supply and exhaust can be balanced independently.

## Mechanical requirement

The route actuator remains one logical servo actuator, but ROUTING-V0.3 models two distinct mechanical air bodies:

- supply_t_diverter: full-area T-diverter between the supply bank and core A/B,
- exhaust_t_diverter: full-area T-diverter between core A/B and the exhaust bank,
- single_servo_linkage: one MZ966 may mechanically couple both shafts,
- position A connects supply → room A and room B → exhaust,
- position B connects supply → room B and room A → exhaust,
- the two air bodies remain physically isolated,
- fan power stays off during all movement.

The previous monolithic V0.2 double-diverter is not the preferred airflow design: its branch area was only about one third of the P12/core airflow area. The control-state semantics do not change with this mechanical correction.

This topology resolves the previous four-logical-role / three-physical-fan ambiguity without assigning one physical fan two simultaneous airflow directions.
