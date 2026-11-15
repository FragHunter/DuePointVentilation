from __future__ import annotations

import cadquery as cq

from hx.parameters import HeatExchangerParameters


def build_p12_fan_pod(
    params: HeatExchangerParameters,
    *,
    depth_mm: float = 25.0,
) -> cq.Workplane:
    """Short modular P12 pod for the 2+1 fan-bank manifold prototype.

    The pod preserves the existing project-modelled P12 aperture and hole pattern
    and keeps each fan electrically/mechanically serviceable as a separate module.
    """
    params.validate()
    if depth_mm <= 0:
        raise ValueError("depth_mm must be positive")

    outer = cq.Workplane("XY").box(
        params.fan_nominal_mm,
        params.fan_nominal_mm,
        depth_mm,
        centered=(True, True, False),
    )
    passage = (
        cq.Workplane("XY")
        .circle(params.fan_aperture_mm / 2.0)
        .extrude(depth_mm)
    )
    pod = outer.cut(passage)

    off = params.fan_hole_spacing_mm / 2.0
    for x in (-off, off):
        for y in (-off, off):
            hole = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(params.fan_hole_diameter_mm / 2.0)
                .extrude(depth_mm)
            )
            pod = pod.cut(hole)

    return pod.clean()


def build_core_routing_adapter(
    params: HeatExchangerParameters,
) -> cq.Workplane:
    """HX-V1.1-compatible routing-manifold interface gauge.

    This intentionally reproduces the sleeve-side flange footprint/opening and
    bolt pattern before the full diverter/manifold transition is committed.
    """
    params.validate()

    flange = cq.Workplane("XY").box(
        params.interface_flange_outer_mm,
        params.interface_flange_outer_mm,
        params.interface_flange_thickness_mm,
        centered=(True, True, False),
    )
    opening = (
        cq.Workplane("XY")
        .rect(params.sleeve_inner_width_mm, params.sleeve_inner_depth_mm)
        .extrude(params.interface_flange_thickness_mm)
    )
    flange = flange.cut(opening)

    off = params.interface_hole_spacing_mm / 2.0
    for x in (-off, off):
        for y in (-off, off):
            hole = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(params.interface_hole_diameter_mm / 2.0)
                .extrude(params.interface_flange_thickness_mm)
            )
            flange = flange.cut(hole)

    return flange.clean()
