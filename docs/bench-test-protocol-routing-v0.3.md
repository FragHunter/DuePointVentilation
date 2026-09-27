# ROUTING-V0.3 full-area T-diverter bench protocol

## Purpose

ROUTING-V0.3 replaces the monolithic V0.2 double-diverter after V0.2 exposed a
branch-port area of only about one third of the P12/core airflow area.

V0.3 uses two separate full-area T-diverters, one for supply and one for
exhaust. A single MZ966 may couple both shafts mechanically.

## Why V0.3

Reference areas:

- V0.2 branch port: 3250 mm2
- P12 112 mm circular aperture: about 9852 mm2
- current core open area: 10000 mm2
- V0.3 square port: 112 x 112 = 12544 mm2

The V0.3 port itself is therefore no longer the obvious minimum-area bottleneck.
Actual pressure loss still has to be measured because the T-turn and flap can
create substantial dynamic loss even with adequate area.

## Parts

- two x ROUTING-V0.3-full-area-t-diverter-body.stl
- two x ROUTING-V0.3-t-diverter-flap-blank.stl after fit parameters are confirmed
- one x ROUTING-V0.3-exhaust-fan-square-transition.stl

Supply common port receives the 112 x 112 V0.2 supply collector outlet.
Exhaust common port connects to fan_3 through the V0.3 round-to-square adapter.
Left/right branch ports later connect to core A/B through final branch adapters.

## Prerequisite measurements

Before final flap/shaft assembly, carry forward the V0.1 results for:

- shaft diameter and printable bearing/bore clearance
- seal material and seat gap
- linkage radius
- loaded MZ966 current and travel time
- P12/core interface corrections

The current 4.4 mm shaft bore remains provisional until those results exist.

## Stage 1 — body inspection

For each T-diverter body check:

- 146 mm outer envelope
- 112 x 112 common port open
- both 112 x 112 branch ports open
- rear wall remains closed
- chamber surfaces have no loose support/stringing
- shaft bore is unobstructed
- no cracking around three large openings

Use one body as supply and one as exhaust; do not join their air cavities.

## Stage 2 — single-body pressure screening

Test one body first without a flap, then with the provisional flap.

At 30 / 50 / 70 / 100 percent fan PWM measure:

- straight reference flow without diverter
- common -> left branch
- common -> right branch
- left branch -> common (reverse/exhaust direction)
- right branch -> common (reverse/exhaust direction)
- static pressure delta where available

The no-flap test separates housing/T-turn loss from flap/seal loss.

## Stage 3 — closed-branch leakage

For each flap position measure or bound:

- intended-branch flow
- closed-branch leakage
- shaft leakage

Repeat in forward and reverse flow. The exhaust diverter must not be assumed to
seal identically merely because the supply direction passed.

## Stage 4 — two-body coupling

Mechanically couple the supply and exhaust diverter shafts to one MZ966 only
after single-body movement is free.

Required logical positions:

Route A:
- supply -> core A
- core B -> exhaust

Route B:
- supply -> core B
- core A -> exhaust

Verify that one servo command moves both bodies into the complementary route
without over-center linkage, binding, or one body reaching a hard stop early.

## Stage 5 — servo current and timing

At 6 V record over at least 20 complete A/B cycles:

- movement peak current
- endpoint current
- A->B travel time
- B->A travel time
- voltage at servo during movement
- body/shaft binding observations
- temperature rise

Production dead-time remains:

fans OFF -> both diverters move -> both stable -> settle margin -> fans ON

## Stage 6 — paired airflow

With both cores connected, measure at 30 / 50 / 70 / 100 percent:

- supply airflow
- exhaust airflow
- core A pressure delta
- core B pressure delta
- supply diverter pressure delta
- exhaust diverter pressure delta
- closed-branch leakage

Use the results to derive supply/exhaust PWM calibration, not equal-PWM
assumptions.

## Exit criteria for final routing revision

- no minimum-area bottleneck below the selected design gate
- acceptable T-turn pressure loss
- quantitative leakage bound
- repeatable complementary route positions
- measured safe servo current and dead-time
- final branch/core adapters defined
- serviceable shaft/seals
- condensate low points/drains defined
