from __future__ import annotations

import cadquery as cq

from .parameters import HeatExchangerParameters


def _box(width: float, depth: float, length: float) -> cq.Workplane:
    return cq.Workplane("XY").box(
        width, depth, length, centered=(True, True, False)
    )


def build_core(params: HeatExchangerParameters) -> cq.Workplane:
    """Build a reinforced straight-channel regenerative matrix.

    The matrix keeps thin internal heat-transfer walls but uses a thicker
    perimeter frame so a removable cartridge has a robust sealing/handling
    surface.
    """

    params.validate()

    w = params.width_mm
    d = params.depth_mm
    L = params.length_mm
    frame = params.perimeter_frame_mm
    wall = params.wall_thickness_mm
    iw = params.matrix_inner_width_mm
    id_ = params.matrix_inner_depth_mm
    cw = params.channel_width_mm
    cd = params.channel_depth_mm

    outer = _box(w, d, L)
    inner_void = _box(iw, id_, L)
    model = outer.cut(inner_void)

    # Internal X-normal walls.
    for i in range(1, params.cells_x):
        x = -iw / 2.0 + i * cw + (i - 0.5) * wall
        part = (
            cq.Workplane("XY")
            .box(wall, id_, L, centered=(True, True, False))
            .translate((x, 0.0, 0.0))
        )
        model = model.union(part)

    # Internal Y-normal walls.
    for j in range(1, params.cells_y):
        y = -id_ / 2.0 + j * cd + (j - 0.5) * wall
        part = (
            cq.Workplane("XY")
            .box(iw, wall, L, centered=(True, True, False))
            .translate((0.0, y, 0.0))
        )
        model = model.union(part)

    return model.clean()
