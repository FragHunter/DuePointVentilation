from __future__ import annotations

import cadquery as cq

from .parameters import HeatExchangerParameters


def _vertical_x_wall(
    x: float,
    width: float,
    depth: float,
    length: float,
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(width, depth, length, centered=(True, True, False))
        .translate((x, 0.0, 0.0))
    )


def _vertical_y_wall(
    y: float,
    width: float,
    depth: float,
    length: float,
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(width, depth, length, centered=(True, True, False))
        .translate((0.0, y, 0.0))
    )


def build_core(params: HeatExchangerParameters) -> cq.Workplane:
    """Build a straight-channel regenerative matrix for pendulum airflow.

    Air flows through the same channels in +Z during one phase and -Z during
    the opposite phase. The printed grid walls provide heat-transfer surface
    and thermal mass.

    This is the core only. Fan routing, seals, condensate handling and bypass
    remain separate mechanical parts.
    """

    params.validate()

    wall = params.wall_thickness_mm
    cw = params.channel_width_mm
    cd = params.channel_depth_mm

    model: cq.Workplane | None = None

    # Walls normal to X.
    for i in range(params.cells_x + 1):
        x = (
            -params.width_mm / 2.0
            + wall / 2.0
            + i * (cw + wall)
        )
        part = _vertical_x_wall(
            x=x,
            width=wall,
            depth=params.depth_mm,
            length=params.length_mm,
        )
        model = part if model is None else model.union(part)

    # Walls normal to Y.
    for j in range(params.cells_y + 1):
        y = (
            -params.depth_mm / 2.0
            + wall / 2.0
            + j * (cd + wall)
        )
        part = _vertical_y_wall(
            y=y,
            width=params.width_mm,
            depth=wall,
            length=params.length_mm,
        )
        model = part if model is None else model.union(part)

    assert model is not None
    return model.clean()
