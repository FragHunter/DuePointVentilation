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

V0.2 airflow-area finding: each monolithic branch port is only about 3250 mm2,
approximately 33 percent of the P12 aperture/core open area. The V0.2
monolithic double-diverter is therefore superseded for airflow development and
should not be printed as the next full-size prototype.

Final shaft/bearing, flap seal, hard stops, servo mount/linkage, branch flanges
and condensate details remain locked behind ROUTING-V0.1 measurements.

The two P12 supply fans use two identical fan-rect-transition parts. The single
exhaust fan can continue using the V0.1 fan-pod interface until its final
exhaust-side transition is defined.


## ROUTING-V0.3

V0.3 replaces the constricted monolithic double-diverter with two separate
full-area T-diverters:

- one full-area T-diverter for supply
- one full-area T-diverter for exhaust
- both remain physically isolated
- one MZ966 may mechanically couple both shafts through linkage
- each common/branch port is 112 x 112 mm

The 112 x 112 mm port area is 12544 mm2, larger than both the modelled P12
112 mm circular aperture (about 9852 mm2) and the current core open area
(10000 mm2).

Also implemented:

- generic vertical-shaft flap blank with hub
- fan_3 round-to-square exhaust transition
- V0.3 tests that reject a return to the V0.2 area restriction

Configuration: routing/prototype-v0.3.yaml

Build command:

PYTHONPATH=. python routing/build_v03.py --config routing/prototype-v0.3.yaml --hx-config parameters.yaml --out exports/ROUTING-V0.3

V0.3 still does not freeze shaft fit, seal geometry, stops, servo linkage,
core-branch flanges or condensate details.
