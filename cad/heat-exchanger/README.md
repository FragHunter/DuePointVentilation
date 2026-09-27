# HX-V1 parametric heat exchanger

This directory contains the first parametric CAD prototype for the DuePointVentilation air-to-air heat exchanger.

## Scope of HX-V1

HX-V1 starts deliberately with the **heat-exchanger core**, not the final installation housing.

Topology:

- alternating cross-flow air channels
- thin separator plates
- edge rails that seal each channel pair
- alternating X/Y flow direction
- fully parameter-driven geometry
- STEP and STL export with CadQuery

The intent is to establish a geometry that can be generated reproducibly, measured and iterated before manifolds, fan adapters, filter holders, condensate tray and servo bypass are frozen.

## Geometry

Each air channel is bounded by two separator plates. Adjacent channels are rotated by 90 degrees:

```text
layer 0  outside/supply stream  X direction  ─────►
layer 1  extract/exhaust stream Y direction       ▲
layer 2  outside/supply stream  X direction  ─────►
layer 3  extract/exhaust stream Y direction       ▲
...
```

The two streams therefore remain separated by printed plates while crossing thermally.

## Build

Create a virtual environment and install the CAD requirements:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Generate the current revision:

```bash
python build.py --config parameters.yaml --out generated
```

Outputs:

- `generated/HX-V1-core.step`
- `generated/HX-V1-core.stl`
- `generated/HX-V1-metadata.json`

Run checks:

```bash
pytest -q
```

GitHub Actions performs the same build and publishes the generated STEP/STL files as a workflow artifact.

## Important prototype limitations

HX-V1 is **not yet a production-ready ventilator**.

Before installation, later revisions must add and validate:

- intake/exhaust plenums
- 120 mm fan/duct adapters
- condensate collection and drain
- removable sealing interfaces
- outside-air filter holder
- inter-stream leak test
- pressure-drop measurement
- actual airflow measurement
- cleaning access
- frost behavior
- optional bypass path and servo damper

The first printed core is a geometry and manufacturing prototype.

## Design rule

Do not optimize only for heat-transfer area. Channel height, surface area, pressure drop and fan operating point must be evaluated together.
