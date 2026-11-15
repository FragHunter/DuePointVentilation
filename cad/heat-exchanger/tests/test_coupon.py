from pathlib import Path

import pytest

from hx import build_core_coupon, load_parameters


ROOT = Path(__file__).resolve().parents[1]


def test_coupon_uses_full_core_channel_geometry() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    coupon = build_core_coupon(p)
    bb = coupon.val().BoundingBox()

    expected_xy = (
        2.0 * p.perimeter_frame_mm
        + 6 * p.channel_width_mm
        + 5 * p.wall_thickness_mm
    )
    assert coupon.val().isValid()
    assert bb.xlen == pytest.approx(expected_xy, abs=1e-3)
    assert bb.ylen == pytest.approx(expected_xy, abs=1e-3)
    assert bb.zlen == pytest.approx(30.0, abs=1e-3)
