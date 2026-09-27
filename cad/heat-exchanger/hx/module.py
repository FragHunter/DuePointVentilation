from __future__ import annotations

import cadquery as cq

from .parameters import HeatExchangerParameters


def _fan_plate(params: HeatExchangerParameters) -> cq.Workplane:
    plate = (
        cq.Workplane("XY")
        .box(
            params.module_outer_mm,
            params.module_outer_mm,
            params.fan_plate_thickness_mm,
            centered=(True, True, False),
        )
    )

    aperture = (
        cq.Workplane("XY")
        .circle(params.fan_aperture_mm / 2.0)
        .extrude(params.fan_plate_thickness_mm)
    )
    plate = plate.cut(aperture)

    offset = params.fan_hole_spacing_mm / 2.0
    for x in (-offset, offset):
        for y in (-offset, offset):
            hole = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(params.fan_hole_diameter_mm / 2.0)
                .extrude(params.fan_plate_thickness_mm)
            )
            plate = plate.cut(hole)

    return plate


def build_module_shell(params: HeatExchangerParameters) -> cq.Workplane:
    """Build the first straight-through dual-fan pendulum module shell.

    One fixed-direction fan is mounted at each end and the two fans face
    opposite directions. Only one fan runs during a pendulum phase.

    This is intentionally a baseline routing concept. The inactive fan remains
    in the airflow path, so its pressure drop must be measured before this
    arrangement can be accepted for a production revision.
    """

    params.validate()

    outer_body = (
        cq.Workplane("XY")
        .box(
            params.module_outer_mm,
            params.module_outer_mm,
            params.module_body_length_mm,
            centered=(True, True, False),
        )
    )

    passage = (
        cq.Workplane("XY")
        .box(
            params.module_passage_width_mm,
            params.module_passage_depth_mm,
            params.module_body_length_mm,
            centered=(True, True, False),
        )
    )

    shell = outer_body.cut(passage)

    room_plate = _fan_plate(params).translate(
        (0.0, 0.0, -params.fan_plate_thickness_mm)
    )
    outside_plate = _fan_plate(params).translate(
        (0.0, 0.0, params.module_body_length_mm)
    )

    return shell.union(room_plate).union(outside_plate).clean()
