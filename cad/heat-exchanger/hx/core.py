from __future__ import annotations

import cadquery as cq

from .parameters import HeatExchangerParameters


def _box(width: float, depth: float, height: float, z0: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(True, True, False))
        .translate((0.0, 0.0, z0))
    )


def build_core(params: HeatExchangerParameters) -> cq.Workplane:
    """Build an alternating cross-flow plate-stack heat-exchanger core.

    Even-numbered channels are open along X. Odd-numbered channels are open
    along Y. Separator plates isolate adjacent streams.

    The model represents the exchanger core only. Plenums, fan adapters,
    condensate tray and bypass are intentionally separate follow-up parts.
    """

    params.validate()

    w = params.width_mm
    d = params.depth_mm
    ch = params.channel_height_mm
    pt = params.plate_thickness_mm
    rt = params.rail_thickness_mm

    model: cq.Workplane | None = None
    z = 0.0

    for channel_index in range(params.channel_count):
        plate = _box(w, d, pt, z)
        model = plate if model is None else model.union(plate)
        z += pt

        if channel_index % 2 == 0:
            # X-flow: rails run along X at the two Y edges.
            y = (d - rt) / 2.0
            rail_a = _box(w, rt, ch, z).translate((0.0, y, 0.0))
            rail_b = _box(w, rt, ch, z).translate((0.0, -y, 0.0))
        else:
            # Y-flow: rails run along Y at the two X edges.
            x = (w - rt) / 2.0
            rail_a = _box(rt, d, ch, z).translate((x, 0.0, 0.0))
            rail_b = _box(rt, d, ch, z).translate((-x, 0.0, 0.0))

        model = model.union(rail_a).union(rail_b)
        z += ch

    final_plate = _box(w, d, pt, z)
    model = final_plate if model is None else model.union(final_plate)

    return model.clean()
