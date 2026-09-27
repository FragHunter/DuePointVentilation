# Servo-routed 2+1 manifold CAD

Parametric validation CAD for the selected topology:

- fan_1 + fan_2: supply bank
- fan_3: exhaust bank
- coupled MZ966 double-diverter swaps room A/B between the two air lanes

## ROUTING-V0.1

Implemented:

- servo-linkage coupon
- horizontal shaft/bearing-clearance coupon
- seal-gap coupon
- modular P12 fan pod
- HX-V1.1 core-routing adapter

Configuration: routing/parameters.yaml

Build command:

PYTHONPATH=. python routing/build.py --config routing/parameters.yaml --hx-config parameters.yaml --out routing/generated

Tracked printable exports: exports/ROUTING-V0.1/

Unknown real-hardware dimensions are not guessed into production geometry. In particular the MZ966 spline is not modelled, the 4 mm shaft family is provisional, the seal slots are measurement gauges, and final servo dead-time depends on loaded travel measurement.
