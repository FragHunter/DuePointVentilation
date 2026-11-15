from __future__ import annotations

import argparse
import json
from pathlib import Path

from cadquery import exporters

from routing import (
    build_linkage_coupon,
    build_seal_gap_coupon,
    build_shaft_clearance_coupon,
    build_p12_fan_pod,
    build_core_routing_adapter,
    load_routing_parameters,
)


def _bbox(shape) -> dict[str, float]:
    bb = shape.val().BoundingBox()
    return {"x": bb.xlen, "y": bb.ylen, "z": bb.zlen}


def _export(shape, out_dir: Path, name: str) -> None:
    exporters.export(shape, str(out_dir / f"{name}.step"))
    exporters.export(shape, str(out_dir / f"{name}.stl"))


def build(config: Path, out_dir: Path, hx_config: Path) -> dict[str, object]:
    params = load_routing_parameters(config)
    from hx import load_parameters
    hx_params = load_parameters(hx_config)

    parts = {
        "servo-linkage-coupon": build_linkage_coupon(params),
        "shaft-clearance-coupon": build_shaft_clearance_coupon(params),
        "seal-gap-coupon": build_seal_gap_coupon(params),
        "p12-fan-pod": build_p12_fan_pod(hx_params),
        "core-routing-adapter": build_core_routing_adapter(hx_params),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    for suffix, shape in parts.items():
        _export(shape, out_dir, f"{params.revision}-{suffix}")

    metadata = {
        "revision": params.revision,
        "purpose": "servo-routed 2+1 manifold validation coupons",
        "parts": {name: _bbox(shape) for name, shape in parts.items()},
        "printer_envelope_mm": {
            "x": params.printer_x_mm,
            "y": params.printer_y_mm,
            "z": params.printer_z_mm,
        },
        "printing": {
            "material": params.material,
            "nozzle_mm": params.nozzle_mm,
            "layer_height_mm": params.layer_height_mm,
        },
        "notes": {
            "servo_spline": "not modelled; linkage coupon bolts to supplied horn",
            "shaft": "4 mm family is provisional until physical hardware is selected",
            "seal": "slot series is a fit gauge; final gasket/seat geometry requires bench data",
        },
    }
    (out_dir / f"{params.revision}-metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("parameters.yaml"),
    )
    parser.add_argument(
        "--hx-config",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "parameters.yaml",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("generated"),
    )
    args = parser.parse_args()
    print(json.dumps(build(args.config, args.out, args.hx_config), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
