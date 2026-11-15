from __future__ import annotations

import argparse
import json
from pathlib import Path

from cadquery import exporters

from hx import load_parameters
from routing import (
    build_diverter_flap_blank,
    build_double_diverter_body,
    build_fan_rect_transition,
    build_supply_merge_collector,
    load_routing_prototype_parameters,
)


def _bbox(shape) -> dict[str, float]:
    bb = shape.val().BoundingBox()
    return {"x": bb.xlen, "y": bb.ylen, "z": bb.zlen}


def _export(shape, out_dir: Path, name: str) -> None:
    exporters.export(shape, str(out_dir / f"{name}.step"))
    exporters.export(shape, str(out_dir / f"{name}.stl"))


def build(config: Path, hx_config: Path, out_dir: Path) -> dict[str, object]:
    p = load_routing_prototype_parameters(config)
    hx = load_parameters(hx_config)

    parts = {
        "fan-rect-transition": build_fan_rect_transition(p, hx),
        "supply-merge-collector": build_supply_merge_collector(p),
        "double-diverter-body": build_double_diverter_body(p),
        "diverter-flap-blank": build_diverter_flap_blank(p),
    }

    # Cache exact CAD bounding boxes before STL tessellation. CadQuery/OCC may
    # mutate the in-memory triangulation/bounding cache during STL export even
    # though the written mesh coordinates remain correct.
    part_bboxes = {name: _bbox(shape) for name, shape in parts.items()}

    out_dir.mkdir(parents=True, exist_ok=True)
    for suffix, shape in parts.items():
        _export(shape, out_dir, f"{p.revision}-{suffix}")

    metadata = {
        "revision": p.revision,
        "purpose": "servo-routed 2+1 manifold geometry proof",
        "parts": part_bboxes,
        "printer_envelope_mm": {
            "x": p.printer_x_mm,
            "y": p.printer_y_mm,
            "z": p.printer_z_mm,
        },
        "topology": {
            "supply_bank": "two P12 fan transitions -> shared merge collector",
            "diverter": "two isolated three-way chambers on one transverse shaft",
            "phase_a": "supply -> core A; core B -> exhaust",
            "phase_b": "supply -> core B; core A -> exhaust",
        },
        "provisional": [
            "collector flow shaping",
            "shaft/bearing fit",
            "flap seal and hard stops",
            "servo mount/linkage",
            "branch flange geometry",
            "condensate details",
        ],
        "printing": {
            "material": p.material,
            "nozzle_mm": p.nozzle_mm,
            "layer_height_mm": p.layer_height_mm,
        },
    }
    (out_dir / f"{p.revision}-metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("prototype-v0.2.yaml"),
    )
    parser.add_argument(
        "--hx-config",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "parameters.yaml",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "exports" / "ROUTING-V0.2",
    )
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.hx_config, args.out), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
