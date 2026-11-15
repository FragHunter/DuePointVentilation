from __future__ import annotations

import cadquery as cq

from .parameters import HeatExchangerParameters


def build_core_coupon(
    params: HeatExchangerParameters,
    *,
    cells_x: int = 6,
    cells_y: int = 6,
    length_mm: float = 30.0,
) -> cq.Workplane:
    """Small print-process coupon with the same channel/wall geometry as the core."""

    params.validate()
    if cells_x < 2 or cells_y < 2 or length_mm <= 0:
        raise ValueError("Invalid coupon dimensions")

    wall = params.wall_thickness_mm
    frame = params.perimeter_frame_mm
    cw = params.channel_width_mm
    cd = params.channel_depth_mm

    inner_w = cells_x * cw + (cells_x - 1) * wall
    inner_d = cells_y * cd + (cells_y - 1) * wall
    width = inner_w + 2.0 * frame
    depth = inner_d + 2.0 * frame

    outer = cq.Workplane("XY").box(
        width, depth, length_mm, centered=(True, True, False)
    )
    inner = cq.Workplane("XY").box(
        inner_w, inner_d, length_mm, centered=(True, True, False)
    )
    model = outer.cut(inner)

    for i in range(1, cells_x):
        x = -inner_w / 2.0 + i * cw + (i - 0.5) * wall
        model = model.union(
            cq.Workplane("XY")
            .box(wall, inner_d, length_mm, centered=(True, True, False))
            .translate((x, 0.0, 0.0))
        )

    for j in range(1, cells_y):
        y = -inner_d / 2.0 + j * cd + (j - 0.5) * wall
        model = model.union(
            cq.Workplane("XY")
            .box(inner_w, wall, length_mm, centered=(True, True, False))
            .translate((0.0, y, 0.0))
        )

    return model.clean()
