# ROUTING-V0.2 geometry-proof bench protocol

## Purpose

ROUTING-V0.2 validates packaging, assembly and first-order airflow behavior of
the selected 2+1 topology after the V0.1 fit coupons establish the real shaft,
seal, P12, linkage and core-interface dimensions.

V0.2 is deliberately not final production geometry. Do not convert its
provisional shaft, flap or rectangular interface dimensions into production
values without recording the corresponding V0.1 measurement.

## Prerequisites

Before treating V0.2 measurements as design input, record from ROUTING-V0.1:

- real P12 fit
- selected horizontal shaft/bore fit
- selected seal/seat gap and seal material
- usable MZ966 linkage radius
- MZ966 loaded travel time and movement current at 6 V
- core-routing flange fit

If a prerequisite is not yet measured, mark the V0.2 result as screening only.

## Parts

Tracked files:

- two x ROUTING-V0.2-fan-rect-transition.stl
- one x ROUTING-V0.2-supply-merge-collector.stl
- one x ROUTING-V0.2-double-diverter-body.stl
- two x ROUTING-V0.2-diverter-flap-blank.stl

Do not force a flap/shaft into the printed diverter if the V0.1 clearance test
selects a different bore family. Update the parameter first.

## Stage 1 — dimensional and assembly check

Record for every print:

- measured X/Y/Z
- visible warp
- layer separation
- flange flatness
- passage obstruction/stringing
- screw/connector access
- mass if available

### Fan transition

Verify:

- P12 frame can be serviced independently
- 112 mm fan-side passage is unobstructed
- rectangular outlet is not visibly collapsed or warped
- two transition modules can be routed to the collector without fan frames colliding

### Supply merge collector

Verify:

- both rectangular inlets accept the transition interface
- center splitter is intact
- splitter terminates before the common chamber
- common outlet is unobstructed
- no trapped print support or loose filament remains inside

### Double diverter

Verify:

- center separator is continuous except at the intentional shaft bore
- left/right chambers do not have a visible direct leakage opening
- both common ports and all four branch ports are open
- two flap blanks can move independently during dry fitting before coupling
- access remains possible for shaft removal and service

## Stage 2 — supply collector pressure screening

Use the same P12 pair and the same power/PWM setup for every comparison.

At 30 / 50 / 70 / 100 percent supply-bank PWM measure:

1. two fans free/open
2. two fans plus individual V0.2 transitions
3. two fans plus transitions plus V0.2 merge collector

Record:

- combined airflow
- static pressure where available
- fan RPM/tach if available
- noise/vibration
- qualitative inlet imbalance between fan 1 and fan 2

The V0.2 collector is a plenum-style merge proof. A significant loss or
fan-to-fan imbalance is a reason to redesign the collector into a smoother Y
transition, not to compensate blindly with higher PWM.

## Stage 3 — diverter leakage screening

Test each chamber separately before coupling both flaps.

For each stable flap end position:

- pressurize the common port
- measure intended-branch airflow
- measure or bound closed-branch leakage
- repeat with flow reversed because the exhaust chamber operates in reverse flow
- inspect shaft penetration leakage

Then test both chambers together and verify there is no supply/exhaust
cross-lane path through the center separator.

If quantitative leakage instrumentation is unavailable, keep the leakage gate
open and record pressure plus smoke/tracer observations as qualitative evidence.

## Stage 4 — coupled route test

After the real shaft/linkage/end stops are incorporated:

Route A:
- supply chamber -> core A branch
- core B branch -> exhaust chamber

Route B:
- supply chamber -> core B branch
- core A branch -> exhaust chamber

For at least 20 A/B cycles record:

- commanded route
- measured servo travel time
- stable endpoint
- movement current
- supply airflow
- exhaust airflow
- closed-branch leakage
- any binding or seal damage

## Stage 5 — interlock

Required sequence:

fans OFF -> servo moves -> endpoint settles -> fans ON

Verify electrically/logically that fan PWM is zero throughout every measured
movement interval.

Production dead-time must come from the worst loaded travel time plus a defined
settling margin unless positive endpoint feedback is added.

## Data

Use cad/heat-exchanger/test-data/templates/routing-v0.2-manifold.csv.

Copy the template to a dated result file; do not overwrite the template.

## Exit criteria for ROUTING-V0.3

Proceed only when:

- V0.1 fit dimensions are recorded
- transition/collector pressure loss is acceptable or a redesign is selected
- diverter chambers remain isolated
- closed-branch leakage has a measured bound
- shaft/flap movement does not bind
- MZ966 current fits the 6 V rail strategy
- safe dead-time is measured
- final branch/core flange orientation is known
- condensate low points and drains are defined
