from __future__ import annotations

import cadquery as cq

from .parameters import HeatExchangerParameters


def build_fit_core_plug(
    params: HeatExchangerParameters,
    *,
    height_mm: float = 20.0,
) -> cq.Workplane:
    """Short solid plug with the exact production core outer footprint."""
    params.validate()
    if height_mm <= 0:
        raise ValueError("height_mm must be positive")
    return (
        cq.Workplane("XY")
        .box(
            params.width_mm,
            params.depth_mm,
            height_mm,
            centered=(True, True, False),
        )
        .clean()
    )


def build_fit_sleeve_ring(
    params: HeatExchangerParameters,
    *,
    height_mm: float = 20.0,
) -> cq.Workplane:
    """Short sleeve section with production insertion clearance."""
    params.validate()
    if height_mm <= 0:
        raise ValueError("height_mm must be positive")

    outer = cq.Workplane("XY").box(
        params.sleeve_outer_mm,
        params.sleeve_outer_mm,
        height_mm,
        centered=(True, True, False),
    )
    inner = cq.Workplane("XY").box(
        params.sleeve_inner_width_mm,
        params.sleeve_inner_depth_mm,
        height_mm,
        centered=(True, True, False),
    )
    return outer.cut(inner).clean()


def build_fan_mount_gauge(
    params: HeatExchangerParameters,
    *,
    plate_thickness_mm: float = 3.0,
) -> cq.Workplane:
    """Minimal 120 mm fan interface gauge before committing to full plenums."""
    params.validate()
    if plate_thickness_mm <= 0:
        raise ValueError("plate_thickness_mm must be positive")

    outer = params.fan_nominal_mm
    gauge = cq.Workplane("XY").box(
        outer,
        outer,
        plate_thickness_mm,
        centered=(True, True, False),
    )
    gauge = gauge.cut(
        cq.Workplane("XY")
        .circle(params.fan_aperture_mm / 2.0)
        .extrude(plate_thickness_mm)
    )

    off = params.fan_hole_spacing_mm / 2.0
    for x in (-off, off):
        for y in (-off, off):
            gauge = gauge.cut(
                cq.Workplane("XY")
                .center(x, y)
                .circle(params.fan_hole_diameter_mm / 2.0)
                .extrude(plate_thickness_mm)
            )

    return gauge.clean()
