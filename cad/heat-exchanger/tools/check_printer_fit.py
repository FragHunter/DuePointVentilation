from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hx import (
    build_core,
    build_core_coupon,
    build_core_sleeve,
    build_gasket,
    build_outside_plenum,
    build_room_plenum,
    load_parameters,
)


def extents(shape):
    b = shape.val().BoundingBox()
    return [b.xlen, b.ylen, b.zlen]


def unique_orientations(dims):
    return sorted(set(itertools.permutations(round(x, 6) for x in dims)))


def fits(dims, usable):
    return all(a <= b + 1e-6 for a, b in zip(dims, usable))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="parameters.yaml")
    ap.add_argument(
        "--printer",
        default="config/printers/anycubic-i3-mega-s.yaml",
    )
    ap.add_argument("--out", default="review/HX-V1.1/printer-fit.json")
    args = ap.parse_args()

    p = load_parameters(args.config)
    pr = yaml.safe_load(Path(args.printer).read_text(encoding="utf-8"))
    printer = pr["printer"]
    build = printer["build_volume_mm"]
    margin = printer["planning_margin_mm"]
    usable = [
        build["x"] - 2 * margin["x"],
        build["y"] - 2 * margin["y"],
        build["z"] - margin["z"],
    ]

    parts = {
        "core": build_core(p),
        "core_coupon": build_core_coupon(p),
        "core_sleeve": build_core_sleeve(p),
        "room_plenum": build_room_plenum(p),
        "outside_plenum": build_outside_plenum(p),
        "gasket": build_gasket(p),
    }

    report = {
        "printer": printer,
        "usable_envelope_mm": {
            "x": usable[0],
            "y": usable[1],
            "z": usable[2],
        },
        "parts": {},
    }

    for name, shape in parts.items():
        dims = extents(shape)
        orientations = [
            o for o in unique_orientations(dims) if fits(o, usable)
        ]
        report["parts"][name] = {
            "native_bbox_mm": dims,
            "fits_with_margin": bool(orientations),
            "fitting_orientations_mm": orientations,
        }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    failed = [
        name for name, value in report["parts"].items()
        if not value["fits_with_margin"]
    ]
    if failed:
        raise SystemExit("Parts do not fit printer: " + ", ".join(failed))


if __name__ == "__main__":
    main()
