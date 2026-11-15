# HX-V1.1 simulation and reasoning review

HX-V1.1 is evaluated with lightweight engineering models before physical printing. These models are intended to find bad design directions early; they are not CFD and not a certified heat-recovery rating.

Generated data and plots live under cad/heat-exchanger/simulation/HX-V1.1/.

## Pressure-drop screening model

The model treats each core passage as a straight square duct and estimates Reynolds number, Darcy friction and a combined entry/exit local loss.

It currently excludes the active fan pressure curve, stopped-fan drag, filter, grille, wall terminal, detailed plenum loss, damper loss and turbulence from fan swirl.

Therefore it is a core-only lower-bound style estimate, not the final module pressure loss.

For the current geometry the model produces approximately:

| Flow per active module | Core-only estimated delta-p |
|---:|---:|
| 10 m3/h | 0.8 Pa |
| 20 m3/h | 1.8 Pa |
| 30 m3/h | 2.9 Pa |
| 40 m3/h | 4.1 Pa |
| 50 m3/h | 5.4 Pa |

This supports keeping the current channel scale for the first physical prototype, but says nothing yet about the stopped P12.

## Simplified regenerative thermal model

The transient model divides the core into axial solid segments and alternates exhaust/supply flow through them.

Included: air sensible heat, solid heat capacity, air-side heat transfer, wall conductivity approximation, alternating flow and repeated cycles to approach periodic operation.

Not included: condensation/evaporation, frost, detailed 3D conduction, fan heat, leakage, imperfect flow distribution and true printed-material properties.

At an illustrative 20 C room / 0 C outdoor condition, 40 m3/h and a 60 s phase, the present PETG-like assumption gives roughly 40 percent simulated supply temperature effectiveness.

This number is only a screening result. It must be replaced by measured values from the prototype.

## Important reasoning findings

### Moisture recovery can work against the drying goal

This is the most important conceptual risk introduced by a pendulum regenerator.

If warm humid exhaust air cools below its dew point inside the storage core, water can condense on the core. In the next supply phase, some of that water can re-evaporate into the incoming air.

That means the device can unintentionally recover moisture, not only heat, reducing net cellar drying performance.

Mitigations to test:

- outward drainage and installation slope,
- hydrophobic/non-sorbing storage surfaces,
- phase-time tuning,
- bypass heat recovery when condensation risk is high,
- monitor inlet/outlet humidity during test operation,
- compare net extracted water with and without the regenerator.

The control system must ultimately optimize net water removal, not just temperature efficiency.

### Same PWM does not guarantee balanced airflow

Two rooms, two modules and four physical fans will have different resistance and fan tolerances. Equal PWM does not imply equal volumetric flow.

The final controller needs per-direction airflow calibration or balancing factors.

### Whole-building balance is not room-level balance

Room A supply plus Room B exhaust can be globally balanced while each room individually experiences pressure.

If doors are closed or transfer paths are small, air may move through leaks instead of the intended route.

Commissioning must include doors open, doors closed and available transfer paths.

### Stopped-fan drag may dominate the core loss

The present axial-opposed baseline is mechanically simple but forces air through the stopped fan.

The core-only pressure-drop estimate is low enough that the stopped fan may become the dominant restriction.

This measurement decides whether HX-V1.x can keep the axial arrangement or must move to parallel branches and dampers.

### Retained/stale actuator commands are a control hazard

MQTT/WLED integration must not allow a stale non-zero command to reappear after reconnect.

The actuator layer should use all-off startup, timestamps/TTL or generation IDs, non-retained transient target commands, retained state only where appropriate, and dead-time before every direction reversal.

### Aqara reporting cadence is not the pendulum clock

The humidity sensors determine whether ventilation is beneficial, but pendulum phase timing must remain local/time-driven in the controller.

The stale-data threshold should be set after observing the real Zigbee reporting cadence, not assumed from the pendulum period.

### The perimeter frame should not be treated as fully active storage

The simplified model uses total solid volume when estimating heat capacity. Some of the thick 3.2 mm perimeter frame is less thermally coupled to the active air channels over one short cycle.

This can overestimate useful storage mass.

The next model iteration should include a participating-solid sensitivity factor or a more detailed conduction model.

## Decision rule for the first prototype

Do not optimize the CAD further from simulation alone.

The first prototype should answer:

1. actual airflow through active plus stopped P12,
2. actual pressure drop,
3. outlet temperature trajectory over each phase,
4. condensation and re-evaporation behavior,
5. real PETG matrix effectiveness,
6. noise,
7. room pressure interaction.

Those measurements determine HX-V1.2.

## Solid-participation sensitivity

The model now also varies how much of the calculated solid heat capacity actually participates in one short pendulum cycle.

For PETG-like assumptions at 40 m3/h and 60 s:

| Participating solid heat capacity | Simulated supply effectiveness |
|---:|---:|
| 50 % | about 37.2 % |
| 75 % | about 39.5 % |
| 100 % | about 40.3 % |

This shows that the first-order result is not extremely sensitive to the thick frame participation under this specific screening condition, but the physical prototype is still required.

The estimated PETG thermal penetration depth over 60 s is about 1.58 mm, while half of the 0.8 mm internal wall is only 0.4 mm. The corresponding half-wall Biot number in the simplified model is about 0.034. That suggests the lumped through-thickness approximation for the thin internal walls is reasonable; the larger uncertainties are flow distribution, stopped-fan restriction, condensation and real material properties.
