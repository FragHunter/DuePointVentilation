import math
from pathlib import Path

import cadquery as cq
import pytest

from hx import load_parameters
from routing import (
    build_exhaust_fan_square_transition,
    build_full_area_t_diverter_body,
    build_t_diverter_flap_blank,
    load_routing_v03_parameters,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "routing" / "prototype-v0.3.yaml"
HX_CONFIG = ROOT / "parameters.yaml"


def _fit(shape, p) -> None:
    solid = shape.val()
    bb = solid.BoundingBox()
    assert solid.isValid()
    assert solid.Volume() > 0
    assert bb.xlen <= p.printer_x_mm
    assert bb.ylen <= p.printer_y_mm
    assert bb.zlen <= p.printer_z_mm


def test_v03_full_area_ports_remove_v02_area_blocker() -> None:
    p = load_routing_v03_parameters(CONFIG)
    hx = load_parameters(HX_CONFIG)

    v03_area = p.diverter_port_mm ** 2
    fan_area = math.pi * (hx.fan_aperture_mm / 2.0) ** 2

    assert v03_area >= fan_area
    assert v03_area >= hx.open_area_mm2
    assert v03_area / 3250.0 > 3.5


def test_full_area_t_diverter_is_valid_and_fits_mega_s() -> None:
    p = load_routing_v03_parameters(CONFIG)
    body = build_full_area_t_diverter_body(p)
    _fit(body, p)

    bb = body.val().BoundingBox()
    assert bb.xlen == pytest.approx(p.diverter_outer_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(p.diverter_outer_mm, abs=1e-3)
    assert bb.zlen == pytest.approx(p.diverter_outer_mm, abs=1e-3)


def test_t_diverter_has_large_open_common_and_branch_ports() -> None:
    p = load_routing_v03_parameters(CONFIG)
    solid = build_full_area_t_diverter_body(p).val()
    half = p.diverter_outer_mm / 2.0

    # Points just inside each intended port must be air/cavity.
    assert not solid.isInside(cq.Vector(0.0, -half + 1.0, 0.0), 1e-6)
    assert not solid.isInside(cq.Vector(-half + 1.0, 0.0, 0.0), 1e-6)
    assert not solid.isInside(cq.Vector(half - 1.0, 0.0, 0.0), 1e-6)

    # Rear wall remains solid; there is deliberately no fourth port.
    assert solid.isInside(cq.Vector(0.0, half - 1.0, 0.0), 1e-6)


def test_t_diverter_flap_blank_is_valid_and_fits_chamber() -> None:
    p = load_routing_v03_parameters(CONFIG)
    flap = build_t_diverter_flap_blank(p)
    _fit(flap, p)
    bb = flap.val().BoundingBox()
    assert bb.zlen == pytest.approx(p.flap_height_mm, abs=1e-3)
    assert p.flap_length_mm + p.flap_hub_outer_mm / 2.0 < p.diverter_inner_mm


def test_exhaust_transition_is_valid_and_full_area_at_outlet() -> None:
    p = load_routing_v03_parameters(CONFIG)
    hx = load_parameters(HX_CONFIG)
    transition = build_exhaust_fan_square_transition(p, hx)
    _fit(transition, p)

    bb = transition.val().BoundingBox()
    assert bb.xlen == pytest.approx(hx.fan_nominal_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(hx.fan_nominal_mm, abs=1e-3)
    assert bb.zlen == pytest.approx(p.exhaust_transition_length_mm, abs=1e-3)
    assert p.exhaust_transition_outlet_mm ** 2 >= hx.open_area_mm2
