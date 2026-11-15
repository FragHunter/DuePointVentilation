# Implementation plan

This project is split into parallel workstreams so hardware, control logic and mechanical development can progress without blocking each other.

## Track A — sensors and psychrometrics

Issue #1 and Issue #5.

1. pair Aqara T1 sensors through Zigbee2MQTT
2. normalize MQTT payloads
3. validate freshness/plausibility
4. calculate dew point and absolute humidity
5. apply drying hysteresis and lockouts
6. feed the result into the pendulum controller

Gate A: automatic ventilation eligibility can be evaluated from recorded test data without physical fans.

## Track B — paired pendulum controller

Issue #4.

1. implement deterministic pair state machine
2. implement PHASE_A / dead-time / PHASE_B
3. keep both modules synchronized
4. guarantee that intake and exhaust are never commanded together inside one module
5. define fault and restart behavior
6. wrap the tested core in Node-RED
7. publish phase/state/reason over MQTT

Gate B: simulated operation can run for many cycles without illegal fan combinations or phase drift.

## Track C — WLED / fan hardware

Issue #6.

1. identify exact GLEDOPTO controller
2. validate the electrical PWM interface to ARCTIC P12 Pro PST
3. determine fan start/minimum PWM
4. determine stopped-fan airflow restriction
5. implement hardware adapter
6. verify safe restart/off behavior

Gate C: one physical module can be driven safely through the logical fan-target interface.

## Track D — regenerative core and module CAD

Issue #2 and PR #3.

1. parametric regenerative core
2. baseline opposed-fan module shell
3. cartridge retention and seals
4. split/serviceable housing
5. condensate drain
6. filter interface
7. wall/window mounting interface
8. compare opposed-fan path against branched/valved routing
9. reserve Miuzei servo interfaces

Gate D: printable module with known airflow path, service access and condensate strategy.

## Track E — heat-recovery test rig

Issue #7.

1. instrument room/outdoor/module temperatures
2. measure airflow and pressure drop
3. test multiple PWM points
4. determine useful phase duration
5. quantify phase-average heat-recovery effectiveness
6. compare printed polymer matrix to alternative storage media if required

Gate E: heat-storage medium and phase time are selected from measurements.

## Track F — system integration

Issue #8.

Integration sequence:

Aqara T1 → Zigbee2MQTT → MQTT → psychrometrics → pendulum FSM → logical fan targets → WLED/GLEDOPTO → two physical room modules → InfluxDB/Grafana.

Production readiness requires all previous gates plus failure-mode tests.

## Current implementation status

Implemented:

- project architecture and roadmap
- Aqara T1 sensor decision
- two-room pendulum architecture
- regenerative core CAD generator
- first opposed-fan module shell
- STEP/STL CI build
- psychrometric calculation library
- ventilation eligibility with hysteresis
- paired pendulum finite-state machine
- unit tests for control core

Next implementation targets:

1. Node-RED wrapper around the control core
2. MQTT topic/schema definition for normalized sensors and fan targets
3. WLED adapter contract
4. CAD cartridge/seal/condensate revision
5. physical fan/interface validation
