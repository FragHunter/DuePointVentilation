# ROUTING-V0.2 geometry-proof exports

Second-stage printable geometry proof for the servo-routed 2+1 fan manifold.

## Parts

Print only after the ROUTING-V0.1 fit coupons have been checked against the
real fan, shaft, seal and servo linkage hardware.

Recommended order:

1. two x ROUTING-V0.2-fan-rect-transition.stl
2. one x ROUTING-V0.2-supply-merge-collector.stl
3. one x ROUTING-V0.2-diverter-flap-blank.stl as a dry-fit sample
4. one x ROUTING-V0.2-double-diverter-body.stl
5. second diverter-flap-blank after shaft/seal fit is confirmed

## Geometry role

- fan-rect-transition: P12 112 mm round airflow aperture to provisional 100 x 48 mm collector interface
- supply-merge-collector: two supply inlets to one 112 x 112 mm common plenum outlet
- double-diverter-body: two isolated three-way chambers sharing a transverse shaft bore
- diverter-flap-blank: one printable flap blank; two are required for the coupled mechanism

## Important limitations

These are not production-frozen parts.

Still measurement-gated:

- exact shaft/bearing clearance
- seal material and seat gap
- flap hard stops
- MZ966 mount and horn/linkage geometry
- final branch/core flanges
- collector pressure-loss optimization
- closed-branch leakage
- condensate drainage details
- production dead-time

All four part types fit the conservative Anycubic i3 Mega S 200 x 200 x 200 mm
project envelope.

Bench protocol: docs/bench-test-protocol-routing-v0.2.md
