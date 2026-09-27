from pathlib import Path

import pytest

from routing import (
    build_linkage_coupon,
    build_seal_gap_coupon,
    build_shaft_clearance_coupon,
    load_routing_parameters,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "routing" / "parameters.yaml"


def _assert_fits_printer(shape, params) -> None:
    bb = shape.val().BoundingBox()
    assert bb.xlen <= params.printer_x_mm
    assert bb.ylen <= params.printer_y_mm
    assert bb.zlen <= params.printer_z_mm


def test_routing_coupon_parameters_validate() -> None:
    params = load_routing_parameters(CONFIG)
    assert params.revision == "ROUTING-V0.1"
    assert params.shaft_bore_diameters_mm == pytest.approx((3.8, 4.0, 4.2, 4.4, 4.6))


@pytest.mark.parametrize(
    "builder",
    [
        build_linkage_coupon,
        build_shaft_clearance_coupon,
        build_seal_gap_coupon,
    ],
)
def test_routing_coupon_is_valid_and_fits_mega_s(builder) -> None:
    params = load_routing_parameters(CONFIG)
    shape = builder(params)
    assert shape.val().isValid()
    assert shape.val().Volume() > 0
    _assert_fits_printer(shape, params)


def test_linkage_coupon_bbox_matches_configuration() -> None:
    params = load_routing_parameters(CONFIG)
    bb = build_linkage_coupon(params).val().BoundingBox()
    assert bb.xlen == pytest.approx(params.linkage_length_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(params.linkage_width_mm, abs=1e-3)
    assert bb.zlen == pytest.approx(params.linkage_thickness_mm, abs=1e-3)


def test_shaft_coupon_has_less_material_than_uncut_block() -> None:
    params = load_routing_parameters(CONFIG)
    shape = build_shaft_clearance_coupon(params)
    full_volume = (
        params.shaft_coupon_length_mm
        * params.shaft_coupon_width_mm
        * params.shaft_coupon_height_mm
    )
    assert shape.val().Volume() < full_volume


def test_seal_coupon_slots_leave_floor() -> None:
    params = load_routing_parameters(CONFIG)
    shape = build_seal_gap_coupon(params)
    bb = shape.val().BoundingBox()
    assert bb.zlen == pytest.approx(params.seal_coupon_height_mm, abs=1e-3)
    assert params.seal_coupon_height_mm - params.seal_slot_depth_mm > 0
