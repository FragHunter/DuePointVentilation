from __future__ import annotations

import argparse
import json
from pathlib import Path

from cadquery import exporters

from hx import (
    build_assembly_compound,
    build_core,
    build_core_sleeve,
    build_gasket,
    build_outside_plenum,
    build_room_plenum,
    load_parameters,
)


def _bbox(shape) -> dict[str, float]:
    bb = shape.val().BoundingBox()
    return {"x": bb.xlen, "y": bb.ylen, "z": bb.zlen}


def _export_pair(shape, out_dir: Path, name: str) -> None:
    exporters.export(shape, str(out_dir / f"{name}.step"))
    exporters.export(shape, str(out_dir / f"{name}.stl"))


def build(config_path: Path, out_dir: Path) -> dict[str, object]:
    p = load_parameters(config_path)

    core = build_core(p)
    sleeve = build_core_sleeve(p)
    room_plenum = build_room_plenum(p)
    outside_plenum = build_outside_plenum(p)
    gasket = build_gasket(p)
    assembly = build_assembly_compound(p)

    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = p.revision

    for suffix, shape in [
        ("core", core),
        ("core-sleeve", sleeve),
        ("room-plenum", room_plenum),
        ("outside-plenum", outside_plenum),
        ("gasket", gasket),
        ("assembly", assembly),
    ]:
        _export_pair(shape, out_dir, f"{prefix}-{suffix}")

    metadata = {
        "revision": p.revision,
        "topology": p.topology,
        "core_dimensions_mm": _bbox(core),
        "sleeve_dimensions_mm": _bbox(sleeve),
        "room_plenum_dimensions_mm": _bbox(room_plenum),
        "outside_plenum_dimensions_mm": _bbox(outside_plenum),
        "assembly_dimensions_mm": _bbox(assembly),
        "matrix": {
            "cells_x": p.cells_x,
            "cells_y": p.cells_y,
            "channel_count": p.channel_count,
            "channel_width_mm": p.channel_width_mm,
            "channel_depth_mm": p.channel_depth_mm,
            "hydraulic_diameter_mm": p.hydraulic_diameter_mm,
            "wall_thickness_mm": p.wall_thickness_mm,
            "perimeter_frame_mm": p.perimeter_frame_mm,
            "open_area_mm2": p.open_area_mm2,
            "open_area_ratio": p.open_area_ratio,
            "gross_internal_surface_area_m2": p.gross_internal_surface_area_m2,
            "approximate_solid_volume_cm3": p.approximate_solid_volume_cm3,
        },
        "operation": {
            "paired_modules": p.paired_modules,
            "phase_time_s": p.phase_time_s,
            "switch_deadtime_s": p.switch_deadtime_s,
        },
        "module": {
            "routing_variant": p.routing_variant,
            "side_clearance_mm": p.side_clearance_mm,
            "sleeve_inner_width_mm": p.sleeve_inner_width_mm,
            "sleeve_outer_mm": p.sleeve_outer_mm,
            "sleeve_length_mm": p.sleeve_length_mm,
            "plenum_length_mm": p.plenum_length_mm,
            "fan_aperture_mm": p.fan_aperture_mm,
            "fan_aperture_area_mm2": p.fan_aperture_area_mm2,
            "matrix_to_fan_area_ratio": p.open_area_mm2 / p.fan_aperture_area_mm2,
            "gasket_nominal_thickness_mm": p.gasket_nominal_thickness_mm,
            "gasket_compressed_thickness_mm": p.gasket_compressed_thickness_mm,
            "gasket_compression_pct": 100.0 * (1.0 - p.gasket_compressed_thickness_mm / p.gasket_nominal_thickness_mm),
            "installation_slope_deg": p.installation_slope_deg,
            "drain_hole_diameter_mm": p.drain_hole_diameter_mm,
            "module_total_length_mm": p.module_total_length_mm,
            "baseline_warning":
                "inactive axial fan remains in airflow path; benchmark pressure drop",
        },
        "printing": {
            "material": p.material,
            "nozzle_mm": p.nozzle_mm,
            "layer_height_mm": p.layer_height_mm,
        },
        "design": {
            "removable_core": p.removable_core,
            "condensate_drain_required": p.condensate_drain_required,
            "reserve_bypass": p.reserve_bypass,
        },
    }
    (out_dir / f"{prefix}-metadata.json").write_text(
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
    print(json.dumps(build(args.config, args.out), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
