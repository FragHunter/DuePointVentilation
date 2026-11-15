from __future__ import annotations

import cadquery as cq

from hx.parameters import HeatExchangerParameters

from .v03_parameters import RoutingV03Parameters


def build_full_area_t_diverter_body(
    params: RoutingV03Parameters,
) -> cq.Workplane:
    """Single-lane full-area T-diverter housing.

    Print two: one for the supply lane and one for the exhaust lane. Each body
    has a front common port and left/right branch ports. This avoids the severe
    area restriction found in the monolithic ROUTING-V0.2 double-diverter.
    """

    params.validate()
    outer = params.diverter_outer_mm
    wall = params.diverter_wall_mm
    inner = params.diverter_inner_mm
    port = params.diverter_port_mm

    body = cq.Workplane("XY").box(
        outer,
        outer,
        outer,
        centered=(True, True, True),
    )

    cavity = cq.Workplane("XY").box(
        inner,
        inner,
        inner,
        centered=(True, True, True),
    )
    body = body.cut(cavity)

    # Front common port on -Y face.
    common = (
        cq.Workplane("XY")
        .box(port, wall + 2.0, port, centered=(True, False, True))
        .translate((0.0, -outer / 2.0 - 1.0, 0.0))
    )
    body = body.cut(common)

    # Full-area branch ports on -X and +X faces.
    left = (
        cq.Workplane("XY")
        .box(wall + 2.0, port, port, centered=(False, True, True))
        .translate((-outer / 2.0 - 1.0, 0.0, 0.0))
    )
    right = (
        cq.Workplane("XY")
        .box(wall + 2.0, port, port, centered=(False, True, True))
        .translate((outer / 2.0 - wall - 1.0, 0.0, 0.0))
    )
    body = body.cut(left).cut(right)

    # Provisional vertical shaft path. Final bearing/seal geometry comes from
    # ROUTING-V0.1 physical clearance measurements.
    shaft = cq.Workplane("XY").circle(
        params.diverter_shaft_bore_mm / 2.0
    ).extrude(outer + 2.0, both=True)
    return body.cut(shaft).clean()


def build_t_diverter_flap_blank(
    params: RoutingV03Parameters,
) -> cq.Workplane:
    """Radial flap blank with a printable shaft hub.

    The hub is intentionally generic: it receives the provisional shaft bore
    and does not model the MZ966 spline or final shaft attachment.
    """

    params.validate()

    plate = (
        cq.Workplane("XY")
        .box(
            params.flap_length_mm,
            params.flap_thickness_mm,
            params.flap_height_mm,
            centered=(False, True, True),
        )
    )

    hub = (
        cq.Workplane("XY")
        .workplane(offset=-params.flap_height_mm / 2.0)
        .circle(params.flap_hub_outer_mm / 2.0)
        .extrude(params.flap_height_mm)
    )
    flap = plate.union(hub)

    bore = (
        cq.Workplane("XY")
        .workplane(offset=-params.flap_height_mm / 2.0 - 1.0)
        .circle(params.diverter_shaft_bore_mm / 2.0)
        .extrude(params.flap_height_mm + 2.0)
    )
    return flap.cut(bore).clean()


def build_exhaust_fan_square_transition(
    params: RoutingV03Parameters,
    hx_params: HeatExchangerParameters,
) -> cq.Workplane:
    """P12 fan-3 adapter to the square common port of the exhaust diverter."""

    params.validate()
    hx_params.validate()

    length = params.exhaust_transition_length_mm
    outer = cq.Workplane("XY").box(
        hx_params.fan_nominal_mm,
        hx_params.fan_nominal_mm,
        length,
        centered=(True, True, False),
    )

    passage = (
        cq.Workplane("XY")
        .circle(hx_params.fan_aperture_mm / 2.0)
        .workplane(offset=length)
        .rect(
            params.exhaust_transition_outlet_mm,
            params.exhaust_transition_outlet_mm,
        )
        .loft(combine=True, ruled=True)
    )
    body = outer.cut(passage)

    # Fan screw holes only need to pass the fan-side wall.
    off = hx_params.fan_hole_spacing_mm / 2.0
    screw_depth = params.exhaust_transition_wall_mm + 1.0
    for x in (-off, off):
        for y in (-off, off):
            body = body.cut(
                cq.Workplane("XY")
                .center(x, y)
                .circle(hx_params.fan_hole_diameter_mm / 2.0)
                .extrude(screw_depth)
            )

    return body.clean()
