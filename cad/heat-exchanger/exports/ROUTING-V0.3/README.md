# ROUTING-V0.3 full-area T-diverter exports

Preferred airflow-development revision after ROUTING-V0.2 exposed a severe
branch-port area restriction.

## Decision

Do not use the V0.2 monolithic double-diverter as the main airflow prototype.

V0.3 uses two physically separate full-area T-diverters:

- print one for supply
- print one for exhaust
- couple both shafts mechanically to one MZ966 if the measured torque/current permits

Each common/branch opening is 112 x 112 mm = 12544 mm2.

For comparison:

- P12 112 mm circular aperture: about 9852 mm2
- current core open area: 10000 mm2
- V0.2 monolithic branch: 3250 mm2

## Parts

- ROUTING-V0.3-full-area-t-diverter-body.stl — print two
- ROUTING-V0.3-t-diverter-flap-blank.stl — print two only after V0.1 shaft/seal fit is confirmed
- ROUTING-V0.3-exhaust-fan-square-transition.stl — fan_3 to exhaust common port

The supply common port receives the 112 x 112 supply collector outlet.

## Still provisional

- shaft/bearing clearance
- seal/seat geometry
- hard stops
- MZ966 coupling/linkage
- core-branch flange adapters
- condensate handling

Bench protocol: docs/bench-test-protocol-routing-v0.3.md
