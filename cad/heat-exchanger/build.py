from __future__ import annotations

import argparse
import json
from pathlib import Path

from cadquery import exporters

from hx import build_core, load_parameters


def build(config_path: Path, out_dir: Path) -> dict[str, object]:
    params = load_parameters(config_path)
    core = build_core(params)

    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = params.revision

    step_path = out_dir / f"{prefix}-core.step"
    stl_path = out_dir / f"{prefix}-core.stl"
    metadata_path = out_dir / f"{prefix}-metadata.json"

    exporters.export(core, str(step_path))
    exporters.export(core, str(stl_path))

    bbox = core.val().BoundingBox()
    metadata = {
        "revision": params.revision,
        "topology": params.topology,
        "dimensions_mm": {
            "x": bbox.xlen,
            "y": bbox.ylen,
            "z": bbox.zlen,
        },
        "channel_count": params.channel_count,
        "x_flow_channels": params.x_flow_channels,
        "y_flow_channels": params.y_flow_channels,
        "x_flow_open_area_mm2": params.x_flow_open_area_mm2,
        "y_flow_open_area_mm2": params.y_flow_open_area_mm2,
        "gross_transfer_area_m2": params.gross_transfer_area_m2,
        "fan_nominal_mm": params.fan_nominal_mm,
        "duct_nominal_mm": params.duct_nominal_mm,
        "printing": {
            "material": params.material,
            "nozzle_mm": params.nozzle_mm,
            "layer_height_mm": params.layer_height_mm,
        },
        "design": {
            "removable_core": params.removable_core,
            "condensate_drain_required": params.condensate_drain_required,
            "reserve_bypass": params.reserve_bypass,
        },
    }
    metadata_path.write_text(
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
        "--out",
        type=Path,
        default=Path(__file__).with_name("generated"),
    )
    args = parser.parse_args()

    metadata = build(args.config, args.out)
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
