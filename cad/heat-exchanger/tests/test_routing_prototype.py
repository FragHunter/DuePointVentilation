from pathlib import Path

import pytest

from hx import load_parameters
from routing import (
    build_diverter_flap_blank,
    build_double_diverter_body,
    build_fan_rect_transition,
    build_supply_merge_collector,
    load_routing_prototype_parameters,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_CONFIG = ROOT / "routing" / "prototype-v0.2.yaml"
HX_CONFIG = ROOT / "parameters.yaml"


def _assert_valid_and_fits(shape, params) -> None:
    solid = shape.val()
    bb = solid.BoundingBox()
    assert solid.isValid()
    assert solid.Volume() > 0
    assert bb.xlen <= params.printer_x_mm
    assert bb.ylen <= params.printer_y_mm
    assert bb.zlen <= params.printer_z_mm


def test_prototype_parameters_validate_and_keep_two_isolated_chambers() -> None:
    p = load_routing_prototype_parameters(PROTOTYPE_CONFIG)
    assert p.revision == "ROUTING-V0.2"
    assert p.diverter_chamber_width_mm > 60
    assert p.diverter_separator_mm >= p.nozzle_mm * 4


def test_fan_rect_transition_is_valid_and_fits_mega_s() -> None:
    p = load_routing_prototype_parameters(PROTOTYPE_CONFIG)
    hx = load_parameters(HX_CONFIG)
    shape = build_fan_rect_transition(p, hx)
    _assert_valid_and_fits(shape, p)
    bb = shape.val().BoundingBox()
    assert bb.xlen == pytest.approx(hx.fan_nominal_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(hx.fan_nominal_mm, abs=1e-3)


def test_supply_merge_collector_is_valid_and_fits_mega_s() -> None:
    p = load_routing_prototype_parameters(PROTOTYPE_CONFIG)
    shape = build_supply_merge_collector(p)
    _assert_valid_and_fits(shape, p)
    bb = shape.val().BoundingBox()
    assert bb.xlen == pytest.approx(p.collector_width_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(p.collector_depth_mm, abs=1e-3)
    assert bb.zlen == pytest.approx(p.collector_length_mm, abs=1e-3)


def test_double_diverter_body_is_valid_and_preserves_outer_envelope() -> None:
    p = load_routing_prototype_parameters(PROTOTYPE_CONFIG)
    body = build_double_diverter_body(p)
    _assert_valid_and_fits(body, p)
    bb = body.val().BoundingBox()
    assert bb.xlen == pytest.approx(p.diverter_width_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(p.diverter_depth_mm, abs=1e-3)
    assert bb.zlen == pytest.approx(p.diverter_height_mm, abs=1e-3)


def test_diverter_flap_blank_fits_one_chamber_with_clearance() -> None:
    p = load_routing_prototype_parameters(PROTOTYPE_CONFIG)
    flap = build_diverter_flap_blank(p)
    _assert_valid_and_fits(flap, p)
    bb = flap.val().BoundingBox()
    assert bb.xlen == pytest.approx(p.diverter_flap_width_mm, abs=1e-3)
    assert bb.xlen < p.diverter_chamber_width_mm
    assert bb.zlen == pytest.approx(p.diverter_flap_length_mm, abs=1e-3)


def test_diverter_body_removes_substantial_air_volume() -> None:
    p = load_routing_prototype_parameters(PROTOTYPE_CONFIG)
    body = build_double_diverter_body(p)
    full = p.diverter_width_mm * p.diverter_depth_mm * p.diverter_height_mm
    assert 0 < body.val().Volume() < full * 0.45


def test_diverter_center_separator_remains_solid_away_from_shaft_bore() -> None:
    import cadquery as cq

    p = load_routing_prototype_parameters(PROTOTYPE_CONFIG)
    solid = build_double_diverter_body(p).val()

    # Center wall must separate the two chambers. Sample away from the common
    # shaft bore, which intentionally pierces the separator at z=0.
    assert solid.isInside(cq.Vector(0.0, 0.0, 20.0), 1e-6)

    chamber_x = p.diverter_separator_mm / 2.0 + p.diverter_chamber_width_mm / 2.0
    assert not solid.isInside(cq.Vector(chamber_x, 0.0, 20.0), 1e-6)


def test_v02_build_metadata_uses_pre_export_exact_bounding_boxes(tmp_path) -> None:
    from routing.build_v02 import build

    metadata = build(PROTOTYPE_CONFIG, HX_CONFIG, tmp_path)
    transition = metadata["parts"]["fan-rect-transition"]

    assert transition["x"] == pytest.approx(120.0, abs=1e-3)
    assert transition["y"] == pytest.approx(120.0, abs=1e-3)
    assert transition["z"] == pytest.approx(64.0, abs=1e-3)
    assert (tmp_path / "ROUTING-V0.2-fan-rect-transition.stl").is_file()
