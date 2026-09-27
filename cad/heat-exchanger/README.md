# HX-V1 parametric regenerative core and module

This directory contains the parametric CAD prototype for a DuePointVentilation **pendulum heat-storage module**.

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

Each module uses a bidirectional regenerative core. Warm outgoing room air heats the core; after the phase reversal, incoming outside air recovers part of that stored heat.

## HX-V1 core

The current core is a square matrix of straight bidirectional channels. The same channels are used in both directions.

Provisional parameters:

- 120 × 120 × 160 mm core
- 18 × 18 channels
- 0.60 mm printed walls
- removable cartridge concept

These are development values, not final production dimensions.

## HX-V1 module shell

A first **axial opposed-fan** housing is now generated around the core:

```text
ROOM
  │
  ▼
[ P12 fan: EXHAUST direction ]
  │
  │ 45 mm plenum
  ▼
[ regenerative core ]
  ▲
  │ 45 mm plenum
  │
[ P12 fan: SUPPLY direction ]
  ▲
  │
OUTSIDE
```

Only one directional fan runs in each phase.

This is deliberately the mechanically simplest baseline. It has one important drawback: the inactive fan remains in the airflow path. We therefore must measure its pressure loss before accepting this topology. If the loss is excessive, the next CAD variant will use parallel fan branches with passive or servo-actuated routing.

Current shell envelope is roughly 129 × 129 × 258 mm before the actual fan bodies, filter, drain and external mounting parts are added.

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
- `generated/HX-V1-module-shell.step`
- `generated/HX-V1-module-shell.stl`
- `generated/HX-V1-metadata.json`

GitHub Actions builds the same artifacts automatically.

## Thermal-storage note

A pendulum exchanger is a regenerator, so thermal storage matters in addition to heat-transfer area and pressure drop.

A fully printed polymer matrix may have insufficient thermal conductivity or heat capacity compared with ceramic or metallic regenerative media. The design stays modular so later revisions can either optimize the printed matrix or retain the printed housing with a different storage insert.

## Next mechanical work

- benchmark pressure drop through an inactive P12 Pro PST
- confirm exact P12 Pro PST mounting dimensions
- add core cartridge stops/seals
- split shell into printable/serviceable halves
- add condensate collection and drain
- add filter interface
- add wall/window mounting interface
- compare axial opposed-fan routing with a branched/damper version
- add future Miuzei servo mounting points
- measure phase-resolved temperatures, airflow and frost behavior

See `docs/heat-exchanger.md`, Issue #2 and Issue #4.
