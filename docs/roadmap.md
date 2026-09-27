# Roadmap

## M0 — Architecture and repository bootstrap

- [x] define two-fan installation model
- [x] select Node-RED as orchestration layer
- [x] select MQTT as internal message bus
- [x] select Aqara Temperature and Humidity Sensor T1 as initial Zigbee environmental sensor
- [x] define Zigbee2MQTT sensor integration
- [x] keep Aqara T1 as initial sensor because hardware is already available
- [ ] identify exact GLEDOPTO WLED PWM controller model
- [ ] verify ARCTIC P12 Pro PST electrical/PWM compatibility
- [ ] define final power architecture
- [ ] define production deployment target for Node-RED/MQTT/InfluxDB

## M1 — Fan hardware proof of concept

Goal: safely control one intake and one exhaust fan through the selected GLEDOPTO/WLED controller.

- [ ] document fan pinout and electrical requirements
- [ ] document controller output topology
- [ ] determine whether native controller output can drive the P12 Pro PST PWM input
- [ ] build adapter/interface circuit if required
- [ ] determine usable PWM frequency/range
- [ ] measure startup threshold
- [ ] measure minimum stable speed
- [ ] verify 0% behavior
- [ ] verify recovery after controller/network restart
- [ ] validate two fans running simultaneously
- [ ] document wiring diagram

**Gate:** no production fan installation until electrical compatibility is confirmed.

## M2 — Zigbee sensor stack

- [ ] select Zigbee coordinator
- [ ] deploy Zigbee2MQTT
- [ ] pair first Aqara T1
- [ ] verify temperature/humidity/pressure reporting
- [ ] verify battery reporting
- [ ] define friendly-name convention
- [ ] normalize Zigbee2MQTT payloads into project sensor schema
- [ ] implement stale-data detection
- [ ] implement plausibility validation
- [ ] compare/calibrate multiple Aqara T1 sensors side-by-side
- [ ] design protected outdoor sensor enclosure / radiation shield

## M3 — Psychrometric engine

- [ ] dew-point calculation
- [ ] absolute-humidity calculation
- [ ] vapor-pressure calculation if needed
- [ ] indoor/outdoor delta calculation
- [ ] condensation-margin calculation
- [ ] unit tests with fixed reference values
- [ ] test boundary conditions
- [ ] define numerical precision and rounding rules

## M4 — Node-RED controller v1

- [ ] sensor ingestion flow
- [ ] normalization flow
- [ ] validation flow
- [ ] psychrometric calculation flow
- [ ] ventilation decision flow
- [ ] state machine
- [ ] hysteresis
- [ ] minimum runtime
- [ ] minimum off-time
- [ ] sensor-fault state
- [ ] manual override with timeout
- [ ] reason codes for every control decision

## M5 — WLED/GLEDOPTO adapter

- [ ] map logical fan target 0–100% to controller output
- [ ] intake fan output
- [ ] exhaust fan output
- [ ] controller availability detection
- [ ] retry/error behavior
- [ ] safe startup state
- [ ] safe state after Node-RED/MQTT loss
- [ ] optional actual-state feedback

## M6 — Active cross ventilation

- [ ] operate intake and exhaust as coordinated pair
- [ ] symmetric speed mode
- [ ] ramp-up / ramp-down
- [ ] configurable minimum fan speed
- [ ] configurable maximum fan speed
- [ ] test room airflow direction
- [ ] test interaction with doors/windows/passive leaks
- [ ] quantify effective airflow if possible

## M6A — 3D-printed heat exchanger

See [heat-exchanger.md](heat-exchanger.md).

- [ ] define target airflow and allowed pressure drop
- [ ] choose exchanger topology (counter-flow / cross-counter-flow)
- [ ] define fan/duct interfaces
- [ ] define maximum core dimensions
- [ ] select print material and print parameters
- [ ] design modular exchanger core
- [ ] provide condensate collection and drain
- [ ] design for inspection and cleaning
- [ ] perform inter-stream air-leak test
- [ ] measure four exchanger temperatures during prototype testing
- [ ] calculate/log temperature effectiveness
- [ ] measure or estimate airflow for each fan-speed point
- [ ] evaluate pressure drop
- [ ] evaluate condensate and frost behavior
- [ ] reserve a mechanical bypass path
- [ ] decide whether the core is removable/replaceable
- [ ] iterate CAD based on measured thermal and airflow performance

## M7 — Multi-installation support

- [ ] configuration-driven zone definitions
- [ ] shared outdoor sensor support
- [ ] independent zone state machines
- [ ] independent manual override
- [ ] controller/channel mapping per zone
- [ ] per-zone thresholds
- [ ] per-zone alarms
- [ ] naming convention for MQTT topics

## M8 — Monitoring and observability

- [ ] InfluxDB schema
- [ ] Grafana dashboards
- [ ] log raw sensor measurements
- [ ] log corrected measurements
- [ ] log calculated dew point
- [ ] log absolute humidity
- [ ] log humidity delta
- [ ] log fan targets
- [ ] log controller states and reason codes
- [ ] log ventilation runtime
- [ ] estimate extracted water mass from airflow × humidity delta × time
- [ ] log heat-exchanger temperatures and effectiveness
- [ ] battery warnings
- [ ] sensor/controller offline alerts

## M9 — Production installation

- [ ] environmental enclosure
- [ ] cable/power safety
- [ ] fan mounting
- [ ] heat-exchanger mounting and condensate drainage
- [ ] protected outside sensor placement
- [ ] commissioning checklist
- [ ] sensor calibration record
- [ ] airflow test
- [ ] failure-mode tests
- [ ] backup/restore procedure
- [ ] operating documentation

## M10 — Miuzei 180° servo dampers

- [ ] mechanical damper design
- [ ] exchanger bypass damper if selected
- [ ] independent 5 V servo supply sizing
- [ ] servo controller selection
- [ ] per-servo open/closed angle calibration
- [ ] OPENING / OPEN / CLOSING / CLOSED states
- [ ] open dampers before fan start
- [ ] stop fan before closing dampers
- [ ] movement timeout/fault handling
- [ ] manual calibration mode

## M11 — Adaptive control

After enough field data exists:

- [ ] fan speed based on absolute-humidity delta
- [ ] airflow model per fan speed
- [ ] extracted-water estimation
- [ ] noise/time-of-day limits
- [ ] optional temperature-loss constraints
- [ ] optional weather input
- [ ] adaptive thresholds based on measured drying performance
