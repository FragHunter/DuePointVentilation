# HX-V1 parametric regenerative core

This directory contains the first parametric CAD prototype for a DuePointVentilation **pendulum heat-storage core**.

## System context

Two ventilation modules are installed in two rooms and work as a synchronized pair:

```text
Phase A:
  Room A = SUPPLY
  Room B = EXHAUST

Phase B:
  Room A = EXHAUST
  Room B = SUPPLY
```

Each module therefore needs a **bidirectional regenerative core**. Warm outgoing room air heats the core; after the phase reversal, incoming outside air recovers part of that stored heat.

HX-V1 now models a straight-channel matrix rather than the earlier simultaneous cross-flow plate concept.

## Geometry

The core is a square matrix of straight bidirectional channels:

```text
room / outside
      │
      ▼
┌─────────────────────┐
│ □ □ □ □ □ □ □ □ □  │
│ □ □ □ □ □ □ □ □ □  │
│ □ □ □ □ □ □ □ □ □  │
│ □ □ □ □ □ □ □ □ □  │
└─────────────────────┘
      │
      ▼
outside / room
```

The same channels are used in both directions.

The current dimensions are provisional. They exist so we can generate, print and measure a first specimen while airflow, installation envelope and material are still being finalized.

## Build

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python build.py --config parameters.yaml --out generated
pytest -q
```

Outputs:

- `generated/HX-V1-core.step`
- `generated/HX-V1-core.stl`
- `generated/HX-V1-metadata.json`

GitHub Actions builds the same artifacts automatically.

## Current prototype assumptions

- 120 mm class fan interface
- one common bidirectional airflow path through each core
- 18 × 18 straight channels
- 160 mm provisional core length
- 0.60 mm provisional printed walls
- removable cartridge concept
- two identical cores, one per room module

These values are **not final design values**.

## Important engineering point

A pendulum exchanger is a **regenerator**, so thermal storage matters in addition to heat-transfer area and pressure drop.

A fully printed polymer matrix may have insufficient heat capacity / conductivity compared with ceramic or metallic regenerative media. HX-V1 deliberately keeps the core modular so that later revisions can either:

1. optimize the printed matrix, or
2. retain the printed housing while using a ceramic/metal/high-thermal-mass insert.

We will decide from measurements rather than assumption.

## Next mechanical work

- intake/exhaust fan routing through the same core
- determine how the inactive fan is isolated from the airflow
- 120 mm fan / 125 mm duct adapters
- condensate collection and drain
- filter interface
- cartridge seals
- future servo-controlled routing/bypass
- pressure-drop and airflow measurement
- phase-resolved temperature measurement
- frost testing

See `docs/heat-exchanger.md` and Issue #2.
