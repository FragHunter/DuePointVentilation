# HX-V1.1 parametric regenerative pendulum module

This directory contains the CadQuery source, tests, simulations, review drawings and generated export workflow for the DuePointVentilation regenerative heat-storage module.

## Architecture

Two room modules operate in opposite phases:

- Phase A: Room A SUPPLY / Room B EXHAUST
- Phase B: Room A EXHAUST / Room B SUPPLY

Each module uses one bidirectional regenerative core.

## Current mechanical revision

HX-V1.1 is modular and serviceable:

- removable 120 x 120 x 160 mm core,
- 6 x 6 / 30 mm core process coupon for printer validation,
- reinforced 3.2 mm cartridge perimeter,
- 0.8 mm internal matrix walls,
- open-ended core sleeve,
- removable room/outside plenums,
- gasket compression,
- condensate drain on outside plenum,
- 120 mm fan interfaces,
- Mega S compatible individual part sizes.

See the documentation under docs for mechanical design, simulation and printing.

## Build

Run pytest, then build.py, generate_sections.py, simulate_hx.py and check_printer_fit.py.

## Design rule

The simulations are screening tools. Final decisions require physical measurements of airflow, inactive-fan drag, heat recovery, moisture behavior and noise.
