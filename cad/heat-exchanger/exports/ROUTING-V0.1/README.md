# ROUTING-V0.1 validation exports

First printable validation set for the servo-routed 2+1 fan manifold.

## Print order

1. ROUTING-V0.1-servo-linkage-coupon.stl
2. ROUTING-V0.1-shaft-clearance-coupon.stl
3. ROUTING-V0.1-seal-gap-coupon.stl
4. ROUTING-V0.1-p12-fan-pod.stl
5. ROUTING-V0.1-core-routing-adapter.stl

Do not print the complete diverter/manifold before these measurements are checked.

## Purpose

- Servo linkage coupon: generic horn-to-linkage test. No unverified MZ966 spline geometry is modelled.
- Shaft clearance coupon: horizontal bore series 3.8 / 4.0 / 4.2 / 4.4 / 4.6 mm around the provisional 4 mm shaft family.
- Seal gap coupon: open slot series 0.6 / 0.8 / 1.0 / 1.2 / 1.4 mm for the real flap-edge/gasket material.
- P12 fan pod: 120 mm footprint, 112 mm aperture, 105 mm hole-spacing model, 4.5 mm holes.
- Core routing adapter: HX-V1.1-compatible 146 mm flange with sleeve opening and 132 mm interface-hole spacing.

## Print assumptions

- Anycubic i3 Mega S
- conservative build envelope 200 x 200 x 200 mm
- PETG
- 0.4 mm nozzle
- 0.20 mm layer height

Record the selected shaft clearance, seal gap, linkage radius, real P12 fit and core-interface fit in Issue #15 before the full coupled diverter is frozen.
