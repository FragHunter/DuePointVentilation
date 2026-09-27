# Anycubic i3 Mega S printing plan

The first physical prototypes are targeted at an Anycubic i3 Mega S.

Manufacturer reference:
https://store.anycubic.com/products/anycubic-i3-mega-s

The manufacturer lists a nominal build volume of 210 x 210 x 205 mm. The project uses a deliberately smaller planning envelope of 200 x 200 x 200 mm (5 mm XY edge margin and 5 mm Z reserve).

## Project printer profile

Source: cad/heat-exchanger/config/printers/anycubic-i3-mega-s.yaml

- nozzle: 0.40 mm
- filament: 1.75 mm
- initial material: PETG
- layer height: 0.20 mm
- explicit line width: 0.40 mm

Temperatures, retraction and speeds are intentionally not frozen yet. They must be tuned on the actual printer/filament combination.

## HX-V1.1 printer-fit result

All individual printable components fit inside the project planning envelope:

| Part | Bounding box |
|---|---:|
| Regenerative core | 120 x 120 x 160 mm |
| Core sleeve | 146 x 146 x 161.6 mm |
| Room plenum | 146 x 146 x 55 mm |
| Outside plenum + drain | about 146 x 147.8 x 55 mm |
| Compressed gasket model | 120 x 120 x 0.8 mm |

The complete assembled module is about 272 mm long and therefore must not be printed as one piece on the Mega S. The modular V1.1 architecture is intentional.

The automated fit result is stored in cad/heat-exchanger/review/HX-V1.1/printer-fit.json.

## Recommended print orientations

### Core

Print with the airflow channels parallel to Z.

Reasons:

- no support inside the 160 mm channels,
- continuous channel walls,
- minimal internal support-removal problem.

The core is tall relative to its wall thickness. A brim should be considered after the first adhesion test.

### Core sleeve

Preferred first test: print upright with one flange on the bed.

The upper flange creates an external overhang and may need local support. This is acceptable for the first prototype but remains a candidate for a support-reduction redesign.

### Plenums

Print with the core-interface flange on the bed. The square-to-round transition then grows toward the fan side.

The room-side plenum must be rotated in the slicer because its assembly coordinate system is mirrored.

The outside plenum has a side drain boss. Local support may be required under the drain. A later revision may use a separately printed drain fitting or a support-free teardrop port.

### Gasket

The CAD gasket represents the compressed geometry, not necessarily the preferred production gasket material.

A closed-cell foam gasket or suitable compliant sealing material may be more reliable than a thin printed PETG part. A TPU test is possible, but the sealing solution should be validated by a leak test.

## Wall strategy

The internal matrix walls are 0.8 mm, i.e. two explicit 0.4 mm lines with the current project line-width assumption.

The outer cartridge frame is 3.2 mm for handling, sealing and service robustness.

Do not let the slicer silently replace the intended 0.8 mm walls with a single variable-width line without checking the preview.

## Before the full core print

Recommended sequence:

1. print the generated HX-V1.1 core coupon first,
2. verify 0.8 mm wall production and channel openness,
3. verify dimensional accuracy,
4. print sleeve/plenum fit pieces,
5. only then print the full 160 mm core.

The full core is likely to be one of the longest print jobs in the project and should not be the first dimensional experiment.


The generated coupon is exported as HX-V1.1-core-coupon.step and HX-V1.1-core-coupon.stl. It preserves the production wall/channel geometry in a much smaller 6 x 6 channel, 30 mm tall test piece.

## Low-cost calibration parts before full prints

The repository now exports three additional calibration parts:

- HX-V1.1-fit-core-plug: short production-size core footprint,
- HX-V1.1-fit-sleeve-ring: short production-clearance sleeve section,
- HX-V1.1-fan-mount-gauge: minimal 120 mm fan-interface gauge.

Use these before printing the full sleeve/plenums. They are intended to catch dimensional shrinkage, clearance errors and P12 mounting assumptions with very little filament and print time.
