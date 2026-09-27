from __future__ import annotations

import argparse
import json
from pathlib import Path

from cadquery import exporters

from hx import build_core, build_module_shell, load_parameters


def _bbox(shape) -> dict[str, float]:
    bb = shape.val().BoundingBox()
    return {"x": bb.xlen, "y": bb.ylen, "z": bb.zlen}


def build(config_path: Path, out_dir: Path) -> dict[str, object]:
    params = load_parameters(config_path)
    core = build_core(params)
    module_shell = build_module_shell(params)

    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = params.revision

    core_step_path = out_dir / f"{prefix}-core.step"
    core_stl_path = out_dir / f"{prefix}-core.stl"
    module_step_path = out_dir / f"{prefix}-module-shell.step"
    module_stl_path = out_dir / f"{prefix}-module-shell.stl"
    metadata_path = out_dir / f"{prefix}-metadata.json"

    exporters.export(core, str(core_step_path))
    exporters.export(core, str(core_stl_path))
    exporters.export(module_shell, str(module_step_path))
    exporters.export(module_shell, str(module_stl_path))

    metadata = {
        "revision": params.revision,
        "topology": params.topology,
        "core_dimensions_mm": _bbox(core),
        "module_shell_dimensions_mm": _bbox(module_shell),
        "matrix": {
            "cells_x": params.cells_x,
            "cells_y": params.cells_y,
            "channel_count": params.channel_count,
            "channel_width_mm": params.channel_width_mm,
            "channel_depth_mm": params.channel_depth_mm,
            "wall_thickness_mm": params.wall_thickness_mm,
            "open_area_mm2": params.open_area_mm2,
            "open_area_ratio": params.open_area_ratio,
            "gross_internal_surface_area_m2":
                params.gross_internal_surface_area_m2,
            "approximate_solid_volume_cm3":
                params.approximate_solid_volume_cm3,
        },
        "operation": {
            "paired_modules": params.paired_modules,
            "phase_time_s": params.phase_time_s,
            "switch_deadtime_s": params.switch_deadtime_s,
        },
        "module": {
            "routing_variant": params.routing_variant,
            "core_clearance_mm": params.core_clearance_mm,
            "shell_wall_mm": params.shell_wall_mm,
            "plenum_length_mm": params.plenum_length_mm,
            "fan_plate_thickness_mm": params.fan_plate_thickness_mm,
            "fan_aperture_mm": params.fan_aperture_mm,
            "fan_hole_spacing_mm": params.fan_hole_spacing_mm,
            "fan_hole_diameter_mm": params.fan_hole_diameter_mm,
            "baseline_warning":
                "inactive axial fan remains in airflow path; benchmark pressure drop",
        },
        "interfaces": {
            "fan_nominal_mm": params.fan_nominal_mm,
            "duct_nominal_mm": params.duct_nominal_mm,
        },
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
