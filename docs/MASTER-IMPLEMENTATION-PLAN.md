# DuePointVentilation — Master implementation plan

See also: [GAP-MATRIX.md](GAP-MATRIX.md) for the current cross-workstream list of open gaps, blockers and physical validation tasks.
See also: [HARDWARE-INVENTORY.md](HARDWARE-INVENTORY.md) for the selected/available hardware and remaining electrical verification items.
See also: [GL-C-211WL-INTEGRATION.md](GL-C-211WL-INTEGRATION.md) for controller-specific fan-interface validation.
See also: [GL-C-211WL-3FAN-TOPOLOGY.md](GL-C-211WL-3FAN-TOPOLOGY.md) for the confirmed single-controller/three-fan architecture and its unresolved role mapping.
See also: [MZ966-SERVO-INTEGRATION.md](MZ966-SERVO-INTEGRATION.md) for servo current sizing, control signal and interlock strategy.

This document is the top-level execution plan for the complete project from sensors and psychrometrics through CAD, printing, fan control, Node-RED orchestration, commissioning and later servo/bypass upgrades.

It intentionally combines the previously separate roadmap, CAD plan, bench protocol and control plan into one ordered checklist with explicit gates.

## 1. Target system

Two ventilation modules are installed in two different rooms and operate as one synchronized pendulum pair.

```text
PHASE A
Room A: outside -> regenerative core -> room      (SUPPLY)
Room B: room    -> regenerative core -> outside   (EXHAUST)

DEAD-TIME: all fan targets OFF

PHASE B
Room A: room    -> regenerative core -> outside   (EXHAUST)
Room B: outside -> regenerative core -> room      (SUPPLY)
```

Control chain:

```text
Aqara T1 sensors
      |
      v
Zigbee2MQTT
      |
      v
MQTT
      |
      v
Node-RED
      |
      +--> psychrometric eligibility
      +--> paired pendulum FSM
      +--> safety / stale data / fault handling
      +--> logical fan targets
      |
      v
WLED / GLEDOPTO adapter
      |
      v
ARCTIC P12 Pro PST fans
```

Mechanical chain per room module:

```text
P12 fan
  |
room plenum
  |
gasket / removable interface
  |
regenerative heat-storage core
  |
gasket / removable interface
  |
outside plenum + condensate drain
  |
P12 fan
```

Future expansion:

```text
Miuzei MZ966 180-degree servos
  |
  +--> bypass damper
  +--> branch/routing damper
  +--> frost/defrost routing
```

---

## 2. Current implementation status

### Main branch

Main currently contains the project architecture, sensor documentation and high-level roadmap.

### CAD branch / PR #3

Branch: `cad/hx-v1`

Current revision: **HX-V1.1**

Implemented there:

- parametric CadQuery regenerative core,
- 18 x 18 channels,
- 120 x 120 x 160 mm core,
- 0.8 mm internal walls,
- 3.2 mm perimeter frame,
- open-ended removable core sleeve,
- separate room and outside plenums,
- gasket model,
- outside condensate drain,
- intended 2 degree outward installation slope,
- Anycubic i3 Mega S printer profile,
- automated printer-fit checks,
- STEP/STL exports,
- section PNG/SVG drawings,
- core pressure-drop screening model,
- simplified regenerative thermal model,
- bench-test CSV format/analyzer,
- small calibration/test prints.

### Control branch / PR #9

Branch: `control/pendulum-v1`

Implemented there:

- dew-point calculation,
- absolute-humidity calculation,
- stale/invalid sensor handling,
- start/stop hysteresis,
- minimum outdoor temperature lockout,
- paired pendulum state machine,
- startup dead-time,
- direction-change dead-time,
- OFF/FAULT safe targets,
- command sequence/TTL/freshness metadata,
- per-room/per-direction PWM trim factors,
- reusable Node-RED wrapper node,
- MQTT contract documentation,
- unit/CI tests.

---

# 3. Complete execution sequence

## Phase 0 — Freeze the physical inventory

### Required actions

- [x] Record controller model: GLEDOPTO GL-C-211WL.
- [ ] Record actual GL-C-211WL hardware revision and installed WLED firmware version.
- [x] Record primary PSU: Mean Well LPV-35-12, 12 V / 3 A / 36 W.
- [x] Record servo DC/DC converter model: LK1263.
- [x] Record LK1263 output: 6 V / 3 A (18 W maximum at stated rating).
- [x] Record servo model: Miuzei MZ966.
- [ ] Verify exact MZ966 operating-voltage range, stall/running current and PWM timing requirements.
- [ ] Verify LK1263 input range/efficiency/thermal derating against the MZ966 load.
- [x] Record physical fan count: three P12 Pro PST fans controlled by one GL-C-211WL.
- [ ] Confirm exact ARCTIC P12 Pro PST variant and physical mounting fit.
- [x] Resolve the mechanical mapping from three physical fans to the four logical roles: **servo-routed 2+1 topology** (fan_1+fan_2 supply bank, fan_3 exhaust bank, coupled diverter swaps room assignment).
- [ ] Confirm current Mega S nozzle is 0.4 mm or update printer profile.
- [ ] Record available PETG brand/material.
- [ ] Record Zigbee coordinator model.
- [ ] Record Node-RED/MQTT host.
- [ ] Record room A and room B dimensions/volume.
- [ ] Record module mounting orientation and available opening dimensions.
- [ ] Record whether condensate can drain directly outside.
- [ ] Record transfer-air path between both rooms when doors are closed.

### Gate 0

No production wiring or final wall-mount CAD is frozen until the exact controller/fan/mechanical inventory is known.

---

## Phase 1 — Mega S dimensional calibration

Use the small generated parts before consuming significant PETG.

Location:

`cad/heat-exchanger/exports/HX-V1.1/`

### Print order

- [ ] `HX-V1.1-core-coupon.stl`
- [ ] `HX-V1.1-fit-core-plug.stl`
- [ ] `HX-V1.1-fit-sleeve-ring.stl`
- [ ] `HX-V1.1-fan-mount-gauge.stl`

### Measure and record

- [ ] coupon outer dimensions,
- [ ] actual 0.8 mm wall thickness,
- [ ] channel openness/stringing,
- [ ] Z straightness over 30 mm,
- [ ] plug outer dimensions,
- [ ] sleeve-ring inner dimensions,
- [ ] real insertion clearance,
- [ ] P12 hole spacing and fit on fan-mount gauge.

### Acceptance

- channels remain open,
- 0.8 mm walls slice/print consistently,
- core plug enters sleeve ring without force but excessive leakage is avoided,
- actual P12 mounting holes fit the gauge.

### Decision

If dimensions differ significantly, update CAD tolerances before printing full parts.

---

## Phase 2 — Electrical GLEDOPTO / P12 proof of concept

Issue: #6

### Required actions

- [ ] Document P12 Pro PST 4-pin pinout.
- [ ] Document exact GLEDOPTO output topology.
- [ ] Determine whether its output is suitable for the fan PWM input directly.
- [ ] If not, design an interface/adapter stage.
- [ ] Verify common ground strategy.
- [ ] Verify fan gets correct continuous supply voltage.
- [ ] Measure PWM frequency/behavior.
- [ ] Determine fan start threshold.
- [ ] Determine minimum stable duty/speed.
- [ ] Verify behavior at 0% target.
- [ ] Verify power-cycle behavior.
- [ ] Verify WLED restart behavior.
- [ ] Verify controller/network loss leaves a safe state.

### Gate 2

The WLED/GLEDOPTO adapter and final wiring diagram must not be frozen until this test passes.

---

## Phase 3 — Aqara T1 / Zigbee2MQTT sensor stack

Issue: #1

### Required actions

- [ ] Install/configure Zigbee coordinator.
- [ ] Install/configure Zigbee2MQTT.
- [ ] Pair indoor sensor room A.
- [ ] Pair indoor sensor room B.
- [ ] Pair outdoor reference sensor.
- [ ] Define stable friendly names.
- [ ] Verify temperature/humidity/pressure reporting.
- [ ] Verify battery reporting.
- [ ] Observe real reporting cadence for several days.
- [ ] Choose stale-data timeout from actual cadence.
- [ ] Side-by-side compare/calibrate sensors.
- [ ] Store offsets separately from raw data.
- [ ] Build outdoor weather/radiation shield for the T1.

### Gate 3

Node-RED must receive normalized valid/stale/invalid sensor data before automatic fan operation is enabled.

---

## Phase 4 — Control-core integration

PR: #9

### Already implemented on branch

- [x] dew point,
- [x] absolute humidity,
- [x] validation,
- [x] hysteresis,
- [x] paired pendulum FSM,
- [x] startup dead-time,
- [x] reversal dead-time,
- [x] fault/off safe outputs,
- [x] TTL/sequence metadata,
- [x] PWM calibration factors,
- [x] Node-RED wrapper skeleton.

### Remaining actions

- [ ] Finish Zigbee2MQTT -> normalized measurement flow.
- [ ] Add production Node-RED flow JSON.
- [ ] Add manual override with timeout.
- [ ] Add degraded-mode policy when one module/controller fails.
- [ ] Add MQTT state/status publishing.
- [ ] Add operator-visible reason codes.
- [ ] Add phase remaining-time telemetry.
- [ ] Add simulation/stress test for many phase cycles.

### Gate 4

A long-running software-only simulation must complete with no illegal simultaneous intake/exhaust command and no phase drift.

---

## Phase 5 — Build the WLED/GLEDOPTO adapter

### Adapter requirements

- [ ] Accept logical target 0..100%.
- [ ] Map logical percentage to actual WLED/GLEDOPTO command.
- [ ] Reject expired commands (`valid_until_ms`).
- [ ] Track command sequence/generation.
- [ ] All outputs OFF on startup.
- [ ] All outputs OFF on reconnect until fresh command arrives.
- [ ] Do not use retained non-zero transient MQTT fan commands.
- [ ] Report actual controller reachability/state.
- [ ] Implement retries without replaying stale commands.
- [ ] Preserve room/module/direction identity in telemetry.

### Gate 5

One physical fan can be safely commanded from the logical control layer without stale-command restart behavior.

---

## Phase 6 — Print HX-V1.1 mechanical parts

Issue: #11

Only after calibration parts pass.

### Print sequence

- [ ] room plenum,
- [ ] outside plenum/drain,
- [ ] core sleeve,
- [ ] verify interfaces/gaskets,
- [ ] full regenerative core.

### Mega S notes

- core channels should be printed parallel to Z,
- inspect slicer preview to ensure 0.8 mm walls are preserved,
- consider brim for tall parts if adhesion testing requires it,
- avoid supports inside the regenerative core channels.

### Mechanical acceptance

- [ ] core is removable,
- [ ] gasket interfaces compress predictably,
- [ ] plenum/sleeve joints can be sealed,
- [ ] condensate drain is unobstructed,
- [ ] installed slope directs water outward,
- [ ] parts remain serviceable and cleanable.

---

## Phase 7 — Airflow and pressure bench tests

Issues: #7, #11

Use the same PWM points for all configurations:

- 30%,
- 50%,
- 70%,
- 100%.

### Test configurations

- [ ] fan alone/open duct,
- [ ] fan + plenum,
- [ ] fan + plenums + empty sleeve,
- [ ] fan + plenums + core,
- [ ] fan + core + stopped opposite P12.

### Record

- airflow m3/h,
- static pressure delta if available,
- PWM,
- RPM/tach if captured,
- sound level,
- vibration/qualitative noise.

Data template:

`cad/heat-exchanger/test-data/templates/hx-v1.1-bench.csv`

Analyzer:

`cad/heat-exchanger/tools/analyze_bench_csv.py`

### Critical decision gate

If stopped-fan drag is too high, do not continue optimizing the axial-opposed architecture. Move to parallel/branched fan routing with dampers.

---

## Phase 8 — Thermal pendulum tests

### Test phase durations

- [ ] 30 s,
- [ ] 45 s,
- [ ] 60 s,
- [ ] 90 s.

### Measure

- room/reference temperature,
- outside/reference temperature,
- module outlet temperature over the complete phase,
- airflow,
- phase state/time.

### Calculate

- instantaneous temperature effectiveness,
- phase-average temperature effectiveness,
- effectiveness versus phase time,
- effectiveness versus airflow.

### Gate 8

Choose the phase duration from measured data, not from the current 60 s placeholder.

---

## Phase 9 — Moisture/condensation test

This is a critical project-specific test because the primary goal is drying, not merely heat recovery.

### Observe

- [ ] where condensation forms,
- [ ] whether it drains,
- [ ] whether water stays trapped in channels,
- [ ] whether humidity rises after phase reversal,
- [ ] whether stored moisture re-evaporates into supply air,
- [ ] net water removal with core,
- [ ] net water removal without/bypassing core.

### Decision rule

Optimize for **net extracted water**, not maximum temperature efficiency.

If moisture re-evaporation is significant, evaluate:

- shorter phase time,
- hydrophobic/non-sorbing core surfaces,
- bypass mode,
- alternative heat-storage insert/material.

---

## Phase 10 — Build and validate the selected fan-routing architecture

Selected architecture: **servo-routed 2+1 fan banks**.

Physical groups:

- fan_1 + fan_2: parallel supply bank,
- fan_3: exhaust bank,
- one logical MZ966 routing actuator moves a coupled double-diverter.

Route A:

- supply bank -> room A,
- room B -> exhaust bank.

Route B:

- supply bank -> room B,
- room A -> exhaust bank.

### Required work

- [x] define the logical 2+1 fan-bank mapping,
- [x] add control-side route/fan-group validation,
- [ ] CAD the separated supply/exhaust plenums and coupled diverter,
- [ ] verify that both airflow paths remain isolated in both positions,
- [ ] measure servo travel time under real damper load,
- [ ] set dead-time >= measured travel + settling margin,
- [ ] validate shared PWM/open-drain signal for fan_1 + fan_2,
- [ ] keep fan_3 on a separately balanceable exhaust PWM group,
- [ ] measure supply-bank vs exhaust-bank flow at 30/50/70/100%,
- [ ] derive per-direction correction factors,
- [ ] verify all fans stay OFF during servo movement.

### Gate 10

Do not freeze final wall CAD or GPIO wiring until route sealing, servo timing, PWM loading and airflow balance pass bench validation.

---

## Phase 11 — Pair balancing between rooms

Equal PWM is not equal airflow.

### Required actions

- [ ] measure room A SUPPLY flow,
- [ ] measure room A EXHAUST flow,
- [ ] measure room B SUPPLY flow,
- [ ] measure room B EXHAUST flow,
- [ ] derive four correction factors,
- [ ] load factors into controller config,
- [ ] verify pair net balance.

Current controller already supports four independent direction trims.

### Also test

- doors open,
- doors closed,
- known transfer grille/door undercut,
- unintended leakage paths.

---

## Phase 12 — Monitoring and observability

### MQTT

Publish at minimum:

- normalized sensor values,
- calculated dew point,
- absolute humidity,
- delta absolute humidity,
- ventilation eligibility,
- reason code,
- pendulum phase,
- sequence/command ID,
- fan targets,
- controller health.

### InfluxDB

Store:

- raw sensor values,
- calibrated sensor values,
- psychrometric values,
- phase transitions,
- fan targets,
- airflow calibration/results,
- heat-recovery effectiveness,
- runtime,
- battery state,
- faults.

### Grafana

Create dashboards for:

- inside/outside T/RH,
- absolute humidity,
- dew point,
- fan targets,
- pendulum phases,
- extracted-water estimate,
- heat-recovery effectiveness,
- alarms/battery.

---

## Phase 13 — Fault-injection and restart tests

### Required tests

- [ ] indoor sensor stale,
- [ ] outdoor sensor stale,
- [ ] Zigbee2MQTT stopped,
- [ ] MQTT broker restart,
- [ ] Node-RED restart,
- [ ] WLED restart,
- [ ] one module controller unreachable,
- [ ] one fan unavailable,
- [ ] stale command after reconnect,
- [ ] power loss during PHASE_A,
- [ ] power loss during PHASE_B,
- [ ] power loss during dead-time.

### Expected safety behavior

- all outputs default OFF,
- only fresh commands are accepted,
- restart enters STARTUP_DEADTIME,
- automatic mode stays disabled if required sensor data is invalid/stale.

---

## Phase 14 — Two-room commissioning

Issue: #8

### Commissioning sequence

1. sensor-only logging,
2. one module manual test,
3. second module manual test,
4. synchronized pendulum test at low PWM,
5. verify airflow direction,
6. verify room pressure/transfer path,
7. enable psychrometric automatic permission,
8. verify shutdown on stale data,
9. verify controller restart behavior,
10. enable logging/alerts,
11. operate under observation before unattended use.

---

## Phase 15 — Filter and wall/window integration

### Mechanical work still required

- [ ] outside-air filter holder,
- [ ] filter pressure-drop measurement,
- [ ] service access for filter replacement,
- [ ] weather hood/exterior terminal,
- [ ] insect screen if required,
- [ ] wall/window mounting adapter,
- [ ] acoustic decoupling,
- [ ] condensate outlet details,
- [ ] thermal bridge/sealing strategy around opening.

Re-run airflow measurements after every filter/grille/terminal change.

---

## Phase 16 — Servo / bypass expansion

Miuzei 180-degree servo phase.

### Mechanical

- [ ] damper geometry,
- [ ] servo mount,
- [ ] hard stops,
- [ ] manual service position,
- [ ] bypass path around regenerative core.

### Electrical

- [x] selected servo supply rail: LK1263 at 6 V / 3 A,
- [ ] measure actual MZ966 idle/movement/stall current; provisional design budget is 2.5 A per active servo at 6 V,
- [x] initial control strategy: 50 Hz RC-servo pulse, 1500 µs neutral, conservative 1000–2000 µs endpoint calibration,
- [x] initial 3 A-rail interlock: move only one servo at a time,
- [ ] verify final calibrated OPEN/CLOSED pulse widths on the real mechanism,
- [ ] common reference where required,
- [ ] peak-current sizing,
- [ ] controller/driver selection.

### Control

- [ ] OPENING,
- [ ] OPEN,
- [ ] CLOSING,
- [ ] CLOSED,
- [ ] movement timeout,
- [ ] fault state,
- [ ] fan interlock.

### Uses

- summer/free cooling,
- heat-recovery bypass for maximum drying,
- frost/defrost,
- maintenance,
- branched fan isolation.

---

## Phase 17 — Adaptive control

Only after field data exists.

Possible improvements:

- fan speed from absolute-humidity delta,
- phase duration from measured core thermal response,
- per-direction airflow closed-loop calibration,
- estimated extracted water per hour/day,
- optimize heat recovery versus net moisture removal,
- noise/time-of-day limits,
- frost prediction,
- weather input,
- adaptive thresholds from measured drying rate.

---

# 4. Immediate next actions

The next practical work should be performed in this order:

1. **Print `HX-V1.1-core-coupon.stl` on the Mega S.**
2. **Print `fit-core-plug` + `fit-sleeve-ring` and measure real clearance.**
3. **Print `fan-mount-gauge` and physically fit the P12 Pro PST.**
4. CAD the **2+1 supply/exhaust plenums + coupled servo diverter**.
5. Perform the **electrical PWM PoC** with one fan, then fan_1 + fan_2 on the candidate shared open-drain PWM signal.
6. Measure the **MZ966 travel time and current at 6 V** with the real diverter load.
7. Pair and log the **Aqara T1 sensors through Zigbee2MQTT**.
8. Finish the **WLED/servo adapter** with TTL/reconnect safety and fan-off-during-servo-motion interlock.
9. Bench-measure **supply-bank vs exhaust-bank airflow** and derive calibration factors.
10. Print plenums/sleeve/full core only after calibration parts and the revised routing CAD pass.

---

# 5. Current major decision gates

## Gate A — printer fit/process

Pass: coupon, clearance pair and fan gauge are dimensionally acceptable.

## Gate B — electrical fan control

Pass: GLEDOPTO/WLED can safely and repeatably control the P12 system.

## Gate C — servo-routed 2+1 airflow architecture

Pass: both diverter positions seal correctly, servo travel fits within safe dead-time, supply/exhaust flow can be balanced, and no fan runs during routing movement.

## Gate D — regenerative core value

Pass: measured heat recovery is useful without unacceptable moisture re-evaporation or pressure loss.

## Gate E — pair balance

Pass: both rooms remain acceptably balanced across both directions and door states.

## Gate F — unattended operation

Pass: all restart/fault/stale-data tests result in a defined safe state.

---

# 6. Important known risks / open questions

- Exact GLEDOPTO model is still required.
- Exact real P12 mount dimensions still need the physical gauge test.
- Stopped-fan drag may dominate total pressure loss.
- PETG may provide only moderate regenerative thermal performance.
- Condensation may re-evaporate and reduce net drying.
- Equal PWM does not guarantee equal room flow.
- Pair-level balance does not guarantee room-level pressure balance.
- Closed doors may require explicit transfer-air openings.
- Outdoor Aqara T1 requires a proper ventilated weather/radiation shield.
- Filter and exterior terminal pressure drop remain unmeasured.
- Frost strategy remains a later field-test item.

---

# 7. Repository map

Main documentation:

- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/sensors.md`
- `docs/heat-exchanger.md`

CAD/HX-V1.1 branch documentation:

- `docs/cad-hx-v1.1.md`
- `docs/cad-review-hx-v1.md`
- `docs/simulation-hx-v1.1.md`
- `docs/printing-anycubic-i3-mega-s.md`
- `docs/bench-test-protocol-hx-v1.1.md`

CAD exports:

- `cad/heat-exchanger/exports/HX-V1.1/`

CAD simulations:

- `cad/heat-exchanger/simulation/HX-V1.1/`

CAD review sections:

- `cad/heat-exchanger/review/HX-V1.1/`

Control branch documentation:

- `docs/control-core.md`
- `docs/mqtt.md`
- `docs/implementation-plan.md`
- `node-red/README.md`

Active work:

- PR #3 — HX-V1.1 CAD/mechanical development
- PR #9 — control core / Node-RED development
- Issue #1 — Aqara/Zigbee2MQTT
- Issue #4 — synchronized pendulum control
- Issue #6 — GLEDOPTO/P12 validation
- Issue #7 — measurement rig
- Issue #8 — system integration
- Issue #10 — HX serviceability blockers / validation
- Issue #11 — Mega S print and bench-test

---

# 8. Definition of done for the first usable system

The first system is considered functionally complete when:

- both Aqara indoor sensors and one outdoor reference are reliable,
- Node-RED receives normalized valid/stale-aware data,
- psychrometric eligibility is tested,
- two modules switch synchronously with dead-time,
- GLEDOPTO/WLED fan control is electrically validated,
- actuator reconnects default safely to OFF,
- both printed modules are serviceable and drain condensate,
- real airflow is measured and direction-balanced,
- stopped-fan architecture has passed or been replaced by dampers,
- heat-recovery and moisture-recovery behavior has been measured,
- InfluxDB/Grafana logging is operational,
- restart/fault tests pass,
- the system can operate unattended without unsafe stale-command behavior.

