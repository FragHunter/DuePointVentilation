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


## ROUTING-V0.2

Second-stage geometry proof. It deliberately keeps all real-hardware-dependent
dimensions provisional while proving that the selected 2+1 topology can be
decomposed into Mega-S-printable modules.

Implemented:

- P12 round-aperture to rectangular collector transition
- two-inlet supply merge collector with short splitter
- two isolated three-way diverter chambers with a common transverse shaft bore
- printable diverter flap blank

Configuration: routing/prototype-v0.2.yaml

Build command:

PYTHONPATH=. python routing/build_v02.py --config routing/prototype-v0.2.yaml --hx-config parameters.yaml --out exports/ROUTING-V0.2

The double-diverter is a topology/packaging proof, not production geometry.
Final shaft/bearing, flap seal, hard stops, servo mount/linkage, branch flanges
and condensate details remain locked behind ROUTING-V0.1 measurements.

The two P12 supply fans use two identical fan-rect-transition parts. The single
exhaust fan can continue using the V0.1 fan-pod interface until its final
exhaust-side transition is defined.
