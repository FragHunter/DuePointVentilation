# ROUTING-V0.1 bench-test protocol

## Purpose

Validate the physical assumptions that intentionally remain open in the servo-routed 2+1 manifold before the complete diverter and collector are frozen.

Do not replace missing measurements with assumed MZ966 spline, shaft, seal or airflow values.

## Stage 1 — print and dimensional inspection

Print the tracked STL files from cad/heat-exchanger/exports/ROUTING-V0.1 in this order:

1. servo-linkage coupon
2. shaft-clearance coupon
3. seal-gap coupon
4. P12 fan pod
5. core-routing adapter

Record printer, PETG, nozzle, layer height, temperatures, measured X/Y/Z dimensions and visible defects.

### Shaft clearance

Test the intended physical rod/bolt in the horizontal bore series 3.8 / 4.0 / 4.2 / 4.4 / 4.6 mm.

Select the smallest bore that rotates freely after cooling and normal screw/fixture loading without unacceptable radial play. Record the actual rod diameter with calipers.

### Seal gap

Test the real flap-edge and gasket/seal material in the 0.6 / 0.8 / 1.0 / 1.2 / 1.4 mm slot series.

Record insertion force, repeatability, visible compression and whether the seal returns after repeated cycles. Do not define the final seat gap until the actual material is tested.

### Linkage

Attach the coupon to the supplied MZ966 horn/linkage hardware. The servo spline itself is intentionally not modelled.

Record the usable linkage radius, screw size, angular range and any collision or over-center condition.

### P12 fan pod

Fit the actual ARCTIC P12 Pro PST. Check aperture, hole spacing, screw clearance, connector/service access and whether the fan frame sits flat.

### Core routing adapter

Check the 146 mm flange, HX-V1.1 sleeve opening and 132 mm interface-hole spacing against the printed/real HX interface.

## Stage 2 — MZ966 electrical/mechanical measurement

Use a regulated 6.0 V source with current measurement and current limiting. The existing 6 V / 3 A LK1263 rail should not be the only instrument used to infer stall current.

Measure at minimum:

- idle current
- no-load motion peak current
- representative damper-load peak current
- route A to route B travel time
- route B to route A travel time
- endpoint current after settling
- supply voltage at the servo during motion
- temperature rise over repeated cycles

A brief controlled current-limit/stall check is optional only if needed; do not hold the servo stalled.

Production fan dead-time must later be at least the worst measured loaded travel time plus settling margin unless positive end-position feedback is added.

## Stage 3 — fan pod / adapter pressure screening

At 30 / 50 / 70 / 100 percent PWM measure:

- fan-alone airflow
- P12 fan-pod airflow
- fan pod plus core-routing adapter airflow
- static pressure delta where instrumentation permits
- noise / vibration notes

This isolates losses introduced by the new modular routing interfaces before the full diverter is built.

## Stage 4 — complete diverter airflow and leakage

After the coupled diverter exists, test both routes separately.

Route A:
- supply bank -> core A
- core B -> exhaust bank

Route B:
- supply bank -> core B
- core A -> exhaust bank

For each route and PWM point record supply airflow, exhaust airflow, pressure deltas and cross-lane leakage.

Leakage must be measured, not judged only by feel. If direct leakage-flow measurement is unavailable, record pressure on the isolated lane plus a clearly documented qualitative smoke/tracer result and keep the quantitative leakage gate open.

## Stage 5 — interlock verification

Instrument or log fan command/state and servo command/state.

Required sequence for every route change:

fans OFF -> servo move -> settle -> fans ON

Verify that no P12 receives a non-zero target while the servo is between stable route positions.

## Data files

Use:

- cad/heat-exchanger/test-data/templates/routing-v0.1-coupon-servo.csv
- cad/heat-exchanger/test-data/templates/routing-v0.1-airflow.csv

Do not overwrite the templates. Copy them to a dated measurement file.

## CAD values unlocked by this test

After measurement, update ROUTING-V0.2 with:

- selected shaft diameter and printed bearing bore
- selected seal/seat gap and gasket material
- selected linkage radius
- real P12 interface corrections if required
- real core-interface corrections if required
- MZ966 calibrated route pulses / angles
- minimum safe switching dead-time
- first pressure-drop and leakage values

Only after those values are recorded should the complete two-fan supply collector and coupled double-diverter be treated as production geometry.
