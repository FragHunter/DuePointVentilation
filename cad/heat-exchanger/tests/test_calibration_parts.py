from pathlib import Path

import pytest

from hx import (
    build_fan_mount_gauge,
    build_fit_core_plug,
    build_fit_sleeve_ring,
    load_parameters,
)


ROOT = Path(__file__).resolve().parents[1]


def test_fit_coupon_has_production_clearance() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    plug = build_fit_core_plug(p)
    ring = build_fit_sleeve_ring(p)

    pb = plug.val().BoundingBox()
    rb = ring.val().BoundingBox()

    assert pb.xlen == pytest.approx(p.width_mm, abs=1e-3)
    assert pb.ylen == pytest.approx(p.depth_mm, abs=1e-3)
    assert rb.xlen == pytest.approx(p.sleeve_outer_mm, abs=1e-3)
    assert p.sleeve_inner_width_mm - p.width_mm == pytest.approx(
        2.0 * p.side_clearance_mm
    )


def test_fan_mount_gauge_matches_modelled_p12_interface() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    gauge = build_fan_mount_gauge(p)
    bb = gauge.val().BoundingBox()

    assert gauge.val().isValid()
    assert bb.xlen == pytest.approx(p.fan_nominal_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(p.fan_nominal_mm, abs=1e-3)
