# CAD concept — servo-routed 2+1 fan topology

## Purpose

This branch develops the mechanical routing required by the selected three-fan architecture without destroying the existing HX-V1.1 axial-opposed benchmark.

The regenerative cores remain bidirectional. The fans move out of the individual room modules and into a shared outside-side manifold.

## System airflow architecture

Each room keeps one regenerative core:

```text
ROOM A <-> CORE A <-> outside-side routing manifold
ROOM B <-> CORE B <-> outside-side routing manifold
```

The routing manifold connects those two core ports to two fixed-direction fan lanes.

### Supply lane

```text
OUTSIDE IN
   |
   +--> P12 fan_1 --+
   |                +--> supply collector --> diverter
   +--> P12 fan_2 --+
```

fan_1 and fan_2 form a parallel supply bank.

### Exhaust lane

```text
diverter --> P12 fan_3 --> OUTSIDE OUT
```

### Route A / PHASE_A

```text
OUTSIDE -> fan_1 + fan_2 -> CORE A -> ROOM A
ROOM B -> CORE B -> fan_3 -> OUTSIDE
```

### Route B / PHASE_B

```text
OUTSIDE -> fan_1 + fan_2 -> CORE B -> ROOM B
ROOM A -> CORE A -> fan_3 -> OUTSIDE
```

No fan reverses electrically.

## Diverter concept

The routing element behaves like a coupled double-pole/double-throw air switch.

Two isolated airflow passages are required:

- one for supply,
- one for exhaust.

The mechanism has two stable positions:

- **A:** supply -> core A and core B -> exhaust
- **B:** supply -> core B and core A -> exhaust

A single Miuzei MZ966 may actuate both internal flaps through a rigid linkage or common shaft.

The supply and exhaust passages must never be joined into one common pressure cavity.

## Transition interlock

Every route change uses:

```text
all fans OFF
  -> move diverter
  -> wait for travel + settling
  -> enable supply/exhaust fan banks
```

The current 3 s software dead-time is only a placeholder. Final dead-time must be derived from the measured MZ966 travel time under the real damper load.

## Reuse from HX-V1.1

Keep as much of the validated core cartridge as possible:

- 120 x 120 x 160 mm regenerative matrix
- removable core sleeve
- gasket interfaces
- condensate-management concept
- interface flange pattern where useful
- Mega S print/process calibration parts

Parts that require redesign for the final 2+1 system:

- room-side fan plate becomes a passive room/grille adapter
- outside-side fan plate becomes a manifold/core adapter
- individual axial opposed fans are removed
- the new common fan manifold and diverter are added

HX-V1.1 remains useful as a pressure-drop and thermal benchmark.

## Mega S packaging constraint

The project uses a conservative 200 x 200 x 200 mm build envelope.

Two 120 mm fan apertures cannot be placed side-by-side on one monolithic printable plate within that envelope.

Therefore the two-fan supply bank must be modular.

Recommended decomposition:

1. supply fan pod A — one P12
2. supply fan pod B — one P12
3. supply merge collector segment(s)
4. exhaust fan pod — one P12
5. core-A routing adapter
6. core-B routing adapter
7. diverter body split into printable halves if needed
8. flap/shaft parts
9. servo mount
10. linkage/horn adapter
11. gaskets/seals

All parts should use bolted/flanged joints so the complete assembly can exceed the printer envelope without requiring one-piece prints.

## First mechanical prototype

Do not print the complete manifold first.

Print small validation parts in this order:

1. **servo-horn/linkage coupon**
   - verify attachment to the supplied MZ966 horn/linkage hardware
   - verify linkage clearance

2. **flap hinge/shaft coupon**
   - verify low-friction motion
   - verify PETG bearing clearance
   - verify no binding after screw tightening

3. **seal-edge coupon**
   - flap edge against gasket/seat
   - measure repeatable closure and leakage

4. **single P12 fan pod**
   - reuse measured fan-hole geometry
   - verify aperture and bolt pattern

5. **single core-to-routing adapter**
   - verify HX-V1.1 flange compatibility

Only after these pass should the full diverter/manifold be generated.

## Provisional geometry rules

Until physical measurements exist:

- preserve at least the current 112 mm fan aperture for each P12
- avoid a sudden contraction directly at the fan
- use smooth merge transitions for the two-fan supply collector
- keep supply and exhaust passages separate by a structural wall
- place the servo outside the wet airflow path where possible
- provide hard mechanical stops independent of servo electronics
- provide a manual/service position
- provide condensate drainage at low points
- avoid trapped pockets where water can collect around the flap shaft

## Fan-bank balance

Two supply fans versus one exhaust fan is intentionally not assumed to be balanced at equal PWM.

Bench measurements must determine:

- supply-bank flow versus PWM
- exhaust-bank flow versus PWM
- core A pressure drop
- core B pressure drop
- diverter pressure drop in both positions
- leakage between supply/exhaust lanes

The control layer already permits different supply/exhaust targets by logical direction. Final calibration values come from these measurements.

## PWM wiring note

fan_1 and fan_2 always receive the same logical supply-bank demand in the current topology, so their PWM inputs are candidates for one shared open-drain control line.

The CAD should still keep both fan connectors serviceable independently.

Do not mechanically bury the connectors or make electrical separation impossible, because the shared PWM arrangement remains bench-gated.

## CAD milestones

### R1 — interface study

- [ ] draw manifold block diagram with core A/B, supply lane and exhaust lane
- [ ] define flange/joint split locations
- [ ] verify every printed component fits 200 x 200 x 200 mm
- [ ] define wet-side drain locations

### R2 — diverter coupon

- [x] model seal-gap/seat validation coupon
- [x] model horizontal shaft/bearing-clearance coupon
- [x] model generic MZ966-horn linkage coupon (no unverified spline geometry)
- [ ] print and measure torque/travel/leakage

### R3 — single-lane prototype

- [x] model one modular P12 fan pod
- [ ] transition/collector
- [x] model one HX-V1.1 core-routing adapter
- [ ] pressure-drop test

### R4 — complete 2+1 manifold

- [ ] dual supply fan bank
- [ ] single exhaust fan bank
- [ ] coupled double diverter
- [ ] both core connections
- [ ] serviceable seals/joints

### R5 — paired-core bench test

- [ ] PHASE_A airflow direction correct
- [ ] PHASE_B airflow direction correct
- [ ] all fans OFF during servo movement
- [ ] no supply/exhaust short circuit
- [ ] acceptable leakage
- [ ] airflow balance calibratable
- [ ] condensate drains safely

## ROUTING-V0.1 printable validation set

Tracked exports are in cad/heat-exchanger/exports/ROUTING-V0.1/.

Print in this order:

1. servo-linkage coupon
2. shaft-clearance coupon
3. seal-gap coupon
4. P12 fan pod
5. core-routing adapter

At creation of ROUTING-V0.1 all five solids build successfully, all fit the conservative 200 x 200 x 200 mm Mega S envelope, and the complete heat-exchanger/routing test suite passes 27/27.

The 4 mm shaft family and seal clearances are deliberately test series rather than final dimensions. The MZ966 spline is deliberately not guessed; the linkage coupon attaches to the supplied physical horn.

## Open measurements before final dimensions

- exact P12 physical fit from fan gauge
- MZ966 body/horn/spline dimensions
- MZ966 loaded travel time
- MZ966 current at 6 V
- required flap torque
- acceptable flap leakage
- actual duct/wall installation envelope

The architecture is fixed; these measurements determine the detailed geometry.
