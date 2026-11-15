from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cadquery as cq
from cadquery import exporters

from hx import build_assembly_compound, build_core, load_parameters


def export_section(shape, plane, height, projection, path):
    wp = cq.Workplane(plane).add(shape.val()).section(height)
    exporters.export(
        wp,
        str(path),
        opt={
            "projectionDir": projection,
            "showAxes": False,
            "strokeWidth": 0.3,
            "width": 1200,
            "height": 900,
            "marginLeft": 20,
            "marginTop": 20,
        },
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="parameters.yaml")
    ap.add_argument("--out", default="review/generated")
    args = ap.parse_args()

    p = load_parameters(args.config)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    core = build_core(p)
    assembly = build_assembly_compound(p)

    export_section(
        core,
        "XY",
        p.length_mm / 2.0,
        (0, 0, 1),
        out / "01_core_XY_mid.svg",
    )
    export_section(
        assembly,
        "XY",
        p.core_start_z_mm + p.length_mm / 2.0,
        (0, 0, 1),
        out / "02_assembly_XY_core_mid.svg",
    )
    export_section(
        assembly,
        "XZ",
        0,
        (0, 1, 0),
        out / "03_assembly_XZ_center.svg",
    )
    export_section(
        assembly,
        "YZ",
        0,
        (1, 0, 0),
        out / "04_assembly_YZ_center.svg",
    )

    room_plate_z = -(
        p.interface_flange_thickness_mm
        + p.plenum_length_mm
        + p.fan_plate_thickness_mm / 2.0
    )
    outside_plate_z = (
        p.sleeve_length_mm
        + p.interface_flange_thickness_mm
        + p.plenum_length_mm
        + p.fan_plate_thickness_mm / 2.0
    )
    export_section(
        assembly,
        "XY",
        room_plate_z,
        (0, 0, 1),
        out / "05_room_end_plate_XY.svg",
    )
    export_section(
        assembly,
        "XY",
        outside_plate_z,
        (0, 0, 1),
        out / "06_outside_end_plate_XY.svg",
    )


if __name__ == "__main__":
    main()
