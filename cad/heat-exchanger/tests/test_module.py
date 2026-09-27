from pathlib import Path

import pytest

from hx import (
    build_assembly_compound,
    build_core_sleeve,
    build_outside_plenum,
    build_room_plenum,
    load_parameters,
    positioned_core,
)


ROOT = Path(__file__).resolve().parents[1]


def test_components_are_valid_solids() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    for part in [
        build_core_sleeve(p),
        build_room_plenum(p),
        build_outside_plenum(p),
        positioned_core(p),
    ]:
        assert part.val().isValid()
        assert len(part.solids().vals()) >= 1


def test_core_does_not_intersect_sleeve() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    intersection = build_core_sleeve(p).intersect(positioned_core(p))
    assert intersection.val().Volume() == pytest.approx(0.0, abs=1e-5)


def test_core_is_insertable_through_open_sleeve() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    assert p.sleeve_inner_width_mm > p.width_mm
    assert p.sleeve_inner_depth_mm > p.depth_mm
    assert p.side_clearance_mm >= 0.6


def test_plenum_retainer_does_not_block_active_matrix() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    assert p.active_core_opening_mm == pytest.approx(
        p.width_mm - 2.0 * p.perimeter_frame_mm
    )


def test_assembly_envelope_is_reasonable() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    assembly = build_assembly_compound(p)
    bb = assembly.val().BoundingBox()
    assert bb.zlen == pytest.approx(p.module_total_length_mm, abs=0.2)
    assert bb.xlen >= p.interface_flange_outer_mm
    assert bb.ylen >= p.interface_flange_outer_mm
