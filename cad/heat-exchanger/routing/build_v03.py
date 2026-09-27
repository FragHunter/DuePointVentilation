from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from cadquery import exporters

from hx import load_parameters
from routing import (
    build_exhaust_fan_square_transition,
    build_full_area_t_diverter_body,
    build_t_diverter_flap_blank,
    load_routing_v03_parameters,
)


def _bbox(shape) -> dict[str, float]:
    bb = shape.val().BoundingBox()
    return {"x": bb.xlen, "y": bb.ylen, "z": bb.zlen}


def _export(shape, out_dir: Path, name: str) -> None:
    exporters.export(shape, str(out_dir / f"{name}.step"))
    exporters.export(shape, str(out_dir / f"{name}.stl"))


def build(config: Path, hx_config: Path, out_dir: Path) -> dict[str, object]:
    p = load_routing_v03_parameters(config)
    hx = load_parameters(hx_config)

    parts = {
        "full-area-t-diverter-body": build_full_area_t_diverter_body(p),
        "t-diverter-flap-blank": build_t_diverter_flap_blank(p),
        "exhaust-fan-square-transition": build_exhaust_fan_square_transition(p, hx),
    }
    bboxes = {name: _bbox(shape) for name, shape in parts.items()}

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, shape in parts.items():
        _export(shape, out_dir, f"{p.revision}-{name}")

    port_area = p.diverter_port_mm ** 2
    fan_area = math.pi * (hx.fan_aperture_mm / 2.0) ** 2

    metadata = {
        "revision": p.revision,
        "decision": "replace monolithic V0.2 double-diverter with two full-area T-diverters",
        "parts": bboxes,
        "quantitative_reason": {
            "v02_branch_area_mm2": 3250.0,
            "p12_aperture_area_mm2": fan_area,
            "v02_branch_vs_p12_pct": 100.0 * 3250.0 / fan_area,
            "v03_port_area_mm2": port_area,
            "v03_port_vs_p12_pct": 100.0 * port_area / fan_area,
            "core_open_area_mm2": hx.open_area_mm2,
            "v03_port_vs_core_pct": 100.0 * port_area / hx.open_area_mm2,
        },
        "topology": {
            "supply": "supply collector -> full-area T-diverter -> core A or core B",
            "exhaust": "core A or core B -> full-area T-diverter -> fan_3",
            "actuation": "one MZ966 may couple the two separate diverter shafts by linkage",
        },
        "printer_envelope_mm": {
            "x": p.printer_x_mm,
            "y": p.printer_y_mm,
            "z": p.printer_z_mm,
        },
        "provisional": [
            "shaft/bearing fit",
            "flap seal",
            "end stops",
            "servo/linkage coupling",
            "core branch flange adapters",
            "condensate handling",
        ],
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
        default=Path(__file__).with_name("prototype-v0.3.yaml"),
    )
    parser.add_argument(
        "--hx-config",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "parameters.yaml",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "exports" / "ROUTING-V0.3",
    )
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.hx_config, args.out), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
