# DuePointVentilation — Gap matrix

Status legend:

- **DONE** — implemented/documented and technically verified at the current level.
- **PARTIAL** — implementation exists, but integration or validation is incomplete.
- **OPEN** — not implemented yet.
- **BLOCKED / INPUT** — requires real hardware, installation data or a user decision before it can be completed.
- **PHYSICAL TEST** — code/CAD may exist, but real-world validation is still required.

This matrix reflects the current project state across `main`, PR #3 (`cad/hx-v1`), PR #9 (`control/pendulum-v1`) and the master-plan branch.

| Area | Item | Status | What exists now | Gap / what is still required | Depends on / source |
|---|---|---|---|---|---|
| Project integration | Merge master plan into main | OPEN | `docs/MASTER-IMPLEMENTATION-PLAN.md` in PR #12 | Review/merge PR #12 so main has the top-level source of truth | PR #12 |
| Project integration | Merge CAD/HX-V1.1 work | PARTIAL | Full HX-V1.1 branch with CAD, exports, simulations, review images | PR #3 is still draft/open; keep unmerged until physical calibration/bench gates are understood or intentionally merge as prototype | PR #3, #11 |
| Project integration | Merge control/Node-RED core | PARTIAL | Control core + Node-RED wrapper on branch | PR #9 still draft/open; WLED adapter and live Node-RED flow are missing | PR #9 |
| Project integration | Keep issues synchronized with reality | OPEN | Issues #1/#2/#4/#5/#6/#7/#8/#10/#11 exist | Several issue checklists do not reflect branch implementations yet; update/close only after merge/validation | Open issues |
| Hardware inventory | Exact GLEDOPTO/WLED controller model | BLOCKED / INPUT | Generic controller abstraction only | Record exact model, hardware revision, WLED version and output topology | Issue #6 |
| Hardware inventory | PSU / power architecture | BLOCKED / INPUT | No final wiring/power design | Record supply voltage, PSU rating, current budget, fusing, connectors, grounding/common reference | M0/M1 |
| Hardware inventory | Exact P12 Pro PST variant/count | BLOCKED / INPUT | Model assumptions + fan gauge CAD | Confirm actual physical fan, connector/pinout, mounting dimensions, quantity per module | #6, #11 |
| Hardware inventory | Mega S nozzle/filament actual setup | BLOCKED / INPUT | Profile assumes 0.4 mm nozzle + PETG | Confirm installed nozzle and actual PETG brand; tune temperatures/retraction/speed | #11 |
| Site data | Room A/B volume | BLOCKED / INPUT | No final room-volume data | Measure room dimensions; derive target air-change/flow range | #2, master plan |
| Site data | Available wall/window opening/envelope | BLOCKED / INPUT | Module envelope known, wall interface not designed | Measure available installation space and wall/opening dimensions | #2, M9 |
| Site data | Transfer-air path between rooms | BLOCKED / INPUT | Risk documented | Measure/define door undercut, grille or leakage path; test doors open/closed | #2, #4 |
| Site data | Condensate disposal path | BLOCKED / INPUT | Drain boss in CAD | Confirm orientation and whether direct drain to outside is possible | #11 |
| Sensors | Zigbee coordinator selected | OPEN | Aqara T1 chosen | Select/record coordinator hardware | #1 |
| Sensors | Zigbee2MQTT deployed | OPEN | Integration architecture documented | Install/configure Zigbee2MQTT and MQTT topics | #1 |
| Sensors | Aqara T1 sensors paired | OPEN | Sensor model documented | Pair room A, room B and outdoor reference sensors | #1 |
| Sensors | Friendly-name/topic convention applied live | PARTIAL | MQTT naming spec exists | Apply stable names in Zigbee2MQTT/Node-RED | #1, docs/mqtt.md |
| Sensors | Sensor normalization flow | PARTIAL | Normalized schema + control input contract exist | Build production Node-RED flow from raw Zigbee2MQTT to normalized sensor messages | #1, PR #9 |
| Sensors | Real reporting cadence measured | OPEN | Stale timeout currently configured generically | Observe real Aqara cadence over days and derive stale threshold | #1 |
| Sensors | Side-by-side sensor calibration | OPEN | Offset model documented | Run sensors together, record offsets/repeatability, store calibration values | #1 |
| Sensors | Outdoor radiation/weather shield | OPEN | Requirement documented | Design/print/install ventilated shield and verify no solar/rain bias | #1 |
| Psychrometrics | Dew point calculation | DONE | Unit-tested JS implementation | Merge PR #9 | #5, PR #9 |
| Psychrometrics | Absolute humidity calculation | DONE | Unit-tested JS implementation | Merge PR #9 | #5, PR #9 |
| Psychrometrics | Stale/invalid sensor handling | DONE | Implemented in control core | Validate with live Zigbee data | #5, PR #9 |
| Psychrometrics | Hysteresis / temperature lockout | DONE | Implemented/configurable | Tune thresholds from field data | #5, PR #9 |
| Control | Paired pendulum FSM | DONE | PHASE_A/B + dead-time FSM | Merge PR #9 and validate long-run behavior | #4, PR #9 |
| Control | Startup/reconnect dead-time | DONE | `STARTUP_DEADTIME` implemented | Validate with real Node-RED/WLED restarts | #4 |
| Control | Command TTL / sequence | DONE | TTL, command ID, transition sequence implemented | Enforce in real WLED adapter | PR #9 |
| Control | Four-direction airflow trims | DONE | room A/B × supply/exhaust calibration factors | Fill with measured values after bench tests | #4, #11 |
| Control | Manual override with timeout | OPEN | Mentioned in architecture only | Implement manual mode + timeout + reason code + safe exit | #4/#8 |
| Control | Degraded mode when one module fails | OPEN | Fault state exists, but pair policy incomplete | Define: stop both vs limited one-sided purge; implement/test | #4 |
| Control | PWM ramp-up/ramp-down | OPEN | Constant targets today | Implement optional ramp if hardware/noise tests require it | #4 |
| Control | Phase remaining-time telemetry | OPEN | Phase/state emitted | Add remaining-time output and MQTT publication | #4 |
| Control | Long-run FSM stress simulation | OPEN | Unit tests cover transitions | Run many cycles, randomized timing/faults/restarts, assert no illegal outputs | #4 |
| Node-RED | Reusable control wrapper node | DONE | `duepoint-control` wrapper on PR #9 | Merge and package/deploy | PR #9 |
| Node-RED | Production importable flow JSON | OPEN | Wrapper + examples only | Build full flow: sensor ingest -> normalize -> control -> actuator -> telemetry | #4/#8 |
| Node-RED | Persistent context policy | OPEN | Node context used | Decide whether context storage is memory/file; restart must intentionally re-enter safe state | #4 |
| MQTT | Topic/schema contract | PARTIAL | `docs/mqtt.md` exists | Apply exact site/module IDs and test with live broker | PR #9 |
| MQTT | Retain policy | PARTIAL | Safety rule documented | Enforce: no retained non-zero transient fan commands | PR #9 |
| WLED/GLEDOPTO | Electrical compatibility with P12 PWM | BLOCKED / INPUT | No real controller characterization | Measure output topology/frequency/levels; decide direct vs adapter circuit | #6 |
| WLED/GLEDOPTO | P12 pinout/wiring diagram | OPEN | Generic fan model only | Document exact 4-pin wiring, 12 V feed, PWM, tach, ground | #6 |
| WLED/GLEDOPTO | Startup/minimum stable PWM | PHYSICAL TEST | No measured curve | Measure start threshold and stable minimum | #6 |
| WLED/GLEDOPTO | 0% behavior | PHYSICAL TEST | Logical OFF exists | Verify actual fan stops and controller output behavior | #6 |
| WLED/GLEDOPTO | Production WLED adapter | OPEN | Logical target contract exists | Implement mapping + TTL reject + reconnect OFF + health/status | #6/#8, PR #9 |
| WLED/GLEDOPTO | Tach/RPM feedback | OPEN / OPTIONAL | Not implemented | Decide whether to capture tach; useful for fan-failure detection/calibration | #6 |
| CAD | Regenerative core geometry | DONE | HX-V1.1 core + STEP/STL | Physical print/process validation still required | PR #3 |
| CAD | Serviceable removable sleeve/plenums | DONE | HX-V1.1 modular CAD | Physical fit/leak validation required | #10/#11 |
| CAD | Gasket/sealing geometry | PARTIAL | Nominal/compressed gasket geometry exists | Select real gasket material and leak-test | #10/#11 |
| CAD | Condensate drain geometry | PARTIAL | Outside plenum drain + 2° intended slope | Physical drain test; confirm install orientation | #10/#11 |
| CAD | Exact P12 fan interface | PARTIAL | Fan-mount gauge exported | Print gauge and physically fit actual P12 | #11 |
| CAD | Filter holder | OPEN | Only listed as future feature | Design filter cassette and measure pressure drop | M9/M15 |
| CAD | Exterior weather hood/terminal | OPEN | None | Design rain/weather termination and insect-screen strategy | M15 |
| CAD | Wall/window mounting adapter | OPEN | None | Design after site opening dimensions are known | M9/M15 |
| CAD | Acoustic decoupling/silencing | OPEN | None | Measure noise first; add gasket/isolator/silencer as needed | #11/M15 |
| CAD | Branched/damper alternative | OPEN | Fallback architecture documented | Create HX-V1.2 branch geometry if stopped-fan drag is excessive | #2/#11 |
| CAD | Servo mount/bypass geometry | OPEN / LATER | Space/use cases documented | Design with Miuzei 180° servo phase | M10 |
| Printing | Core process coupon | PHYSICAL TEST | STL/STEP exported | Print on Mega S; inspect walls/channels/stringing/dimensions | #11 |
| Printing | Core/sleeve clearance gauges | PHYSICAL TEST | Plug/ring STL/STEP exported | Print and measure actual clearance/shrinkage | #11 |
| Printing | Fan-mount gauge | PHYSICAL TEST | STL/STEP exported | Print and fit P12 | #11 |
| Printing | Full plenums/sleeve | OPEN after gate | Printable models exist | Print only after calibration parts pass | #11 |
| Printing | Full 120×120×160 core | OPEN after gate | STL/STEP exists | Print only after process/fit checks pass | #11 |
| Printing | Final slicer profile | OPEN | Starting Mega S/PETG profile documented | Tune temp, speed, retraction, brim/support strategy and save profile | #11 |
| Bench instrumentation | Airflow measurement method | OPEN | Bench protocol expects airflow | Select/calibrate anemometer/duct method or flow hood | #7/#11 |
| Bench instrumentation | Differential pressure measurement | OPEN | Optional in protocol | Select manometer/pressure sensor + tap geometry | #7 |
| Bench instrumentation | Fast phase temperature sensors | OPEN | Four-temperature concept documented | Aqara is too slow for phase-resolved transient testing; select fast wired probes/thermistors | #7 |
| Bench instrumentation | Phase-resolved humidity sensors | OPEN | Moisture risk documented | Select sufficiently fast RH method for re-evaporation testing | #7/#11 |
| Bench | Baseline fan-only airflow curve | PHYSICAL TEST | Protocol/data template exists | Measure 30/50/70/100% PWM | #7/#11 |
| Bench | Core pressure-drop curve | PHYSICAL TEST | Simulation exists | Measure actual core+module pressure/flow | #7/#11 |
| Bench | Stopped-fan drag | PHYSICAL TEST / CRITICAL | Major risk identified | Measure airflow through inactive opposite P12 | #6/#7/#11 |
| Bench | Thermal phase sweep | PHYSICAL TEST | Simulation + CSV analyzer exist | Test 30/45/60/90 s, calculate phase-average effectiveness | #7/#11 |
| Bench | Condensation/drain test | PHYSICAL TEST / CRITICAL | Drain designed | Confirm water reaches drain and does not pool in channels | #11 |
| Bench | Moisture re-evaporation test | PHYSICAL TEST / CRITICAL | Risk identified | Measure outlet RH after reversal and net water removal | #11 |
| Bench | Noise/vibration | PHYSICAL TEST | Protocol mentions it | Measure/record and decide acoustic changes | #11 |
| Simulation | Core-only pressure model | DONE / SCREENING | CSV + plot | Replace assumptions with measured fan/system data | PR #3 |
| Simulation | Simplified regenerative thermal model | DONE / SCREENING | Transient model + sensitivity plots | Calibrate against measurements; real PETG properties | PR #3 |
| Simulation | Stopped-fan model | OPEN | Not modeled | Add only after measured fan restriction exists | #7 |
| Simulation | Condensation/frost model | OPEN / LATER | Not modeled | Add only if field data justifies it | M6A |
| Pair balancing | Four measured directional flows | OPEN | Controller trim support exists | Measure A/B supply/exhaust and derive trims | #4/#11 |
| Pair balancing | Door open/closed pressure behavior | PHYSICAL TEST | Risk documented | Test transfer path and leakage | #4/#11 |
| Monitoring | InfluxDB schema/deployment | OPEN | Data list documented | Create DB/bucket/retention + write nodes | M8/#8 |
| Monitoring | Grafana dashboards | OPEN | Desired metrics documented | Build dashboards for sensors, AH, dew point, phases, fans, faults | M8 |
| Monitoring | Extracted-water estimate | OPEN | Formula concept documented | Requires calibrated airflow; implement after bench data | M8/M11 |
| Monitoring | Alerts | OPEN | Desired alarms documented | Sensor stale, controller offline, battery, fan fault | M8 |
| Safety/fault | MQTT broker restart test | OPEN | Safety strategy documented | Run real fault injection | M9/#8 |
| Safety/fault | Node-RED restart test | OPEN | STARTUP_DEADTIME exists | Validate end-to-end OFF/restart behavior | #8 |
| Safety/fault | WLED restart/network-loss test | OPEN | TTL strategy exists | Validate physical output stays/goes OFF safely | #6/#8 |
| Safety/fault | One-controller/module failure policy | OPEN | Generic fault state exists | Implement degraded policy and test | #4/#8 |
| Safety/fault | Fan-failure detection | OPEN | No tach/flow health logic yet | Decide tach/RPM or inferred failure method | #6/#8 |
| Safety/fault | Frost behavior/defrost | OPEN / LATER | Risk documented | Field-test cold conditions; design bypass/defrost if needed | M6A/M10 |
| Installation | Final enclosure/environmental protection | OPEN | Module CAD only | Electronics enclosure, cable glands, strain relief, ingress strategy | M9 |
| Installation | Exterior filter/insect screen | OPEN | None | Design/install and re-measure flow | M15 |
| Installation | Thermal bridge/weather sealing at wall | OPEN | None | Define wall/window installation details | M15 |
| Installation | Two-module physical commissioning | OPEN | Commissioning plan exists | Install and test pair in both rooms | #8 |
| Documentation | BOM | OPEN | Hardware list is distributed across docs | Create one BOM with quantities/specs/substitutions | M0/M9 |
| Documentation | Final wiring diagram | OPEN | Not yet possible | Produce after GLEDOPTO/P12 electrical PoC | #6 |
| Documentation | Assembly instructions | OPEN | CAD docs exist | Step-by-step printed module assembly + gasket/drain/fan orientation | #11 |
| Documentation | Calibration procedure | PARTIAL | Bench/print protocols exist | Add Aqara calibration + airflow trim procedure in one operator guide | #1/#11 |
| Documentation | Operating/troubleshooting guide | OPEN | Architecture docs only | Manual override, alarms, recovery, maintenance, filter/core cleaning | M9 |
| Deployment | Node-RED/MQTT host finalized | BLOCKED / INPUT | Software architecture exists | Record production host/container strategy | M0 |
| Deployment | Backup/restore | OPEN | None | Back up flows, config, Zigbee2MQTT, MQTT, Influx/Grafana | M9 |
| Deployment | Release packaging/versioning | OPEN | Branch exports exist | Define first release/tag after prototype validation | Project integration |
| Servos | Servo supply/controller selection | OPEN / LATER | Miuzei 180° planned | Size 5 V supply, choose driver/controller | M10 |
| Servos | Damper FSM/interlocks | OPEN / LATER | Desired states documented | Implement OPENING/OPEN/CLOSING/CLOSED + fan interlock | M10 |
| Adaptive control | Dynamic fan speed from humidity delta | OPEN / LATER | Static PWM today | Implement after airflow calibration/field data | M11 |
| Adaptive control | Adaptive phase duration | OPEN / LATER | 60 s is placeholder | Tune from measured thermal/moisture performance | M11 |
| Adaptive control | Net-water-removal optimization | OPEN / LATER | Key objective documented | Combine AH delta, calibrated flow, heat-recovery/moisture behavior | M11 |

## Critical-path gaps

The project can progress in software and CAD, but the following items are the main gates that cannot be solved purely in code:

1. **Exact GLEDOPTO model and electrical PWM compatibility.**
2. **Mega S calibration prints and real P12 fan fit.**
3. **Real airflow through the stopped opposite P12.**
4. **Fast instrumentation for phase-resolved temperature/humidity tests.**
5. **Condensation/re-evaporation measurement to prove net drying performance.**
6. **Room dimensions and transfer-air behavior with doors closed.**
7. **Live Zigbee2MQTT/Aqara integration and real reporting cadence.**

## Immediate priority order

1. Fill hardware/site inventory gaps.
2. Print core coupon + clearance pair + fan gauge.
3. Perform GLEDOPTO/P12 electrical proof of concept.
4. Deploy/pair Aqara sensors with Zigbee2MQTT.
5. Select fast bench sensors + airflow/pressure measurement method.
6. Print plenums/sleeve after calibration passes.
7. Measure stopped-fan drag before printing/committing to two full modules.
8. Run thermal + moisture bench tests.
9. Finish production WLED adapter and full Node-RED flow.
10. Build monitoring/fault-injection/commissioning path.
