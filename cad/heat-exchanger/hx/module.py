from __future__ import annotations

import cadquery as cq

from .parameters import HeatExchangerParameters


def _square_ring(
    outer_mm: float,
    inner_mm: float,
    thickness_mm: float,
) -> cq.Workplane:
    outer = cq.Workplane("XY").box(
        outer_mm, outer_mm, thickness_mm, centered=(True, True, False)
    )
    inner = cq.Workplane("XY").box(
        inner_mm, inner_mm, thickness_mm, centered=(True, True, False)
    )
    return outer.cut(inner)


def _interface_flange(
    params: HeatExchangerParameters,
    *,
    inner_opening_mm: float,
) -> cq.Workplane:
    flange = _square_ring(
        params.interface_flange_outer_mm,
        inner_opening_mm,
        params.interface_flange_thickness_mm,
    )
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
    return flange


def _fan_plate(params: HeatExchangerParameters) -> cq.Workplane:
    plate = (
        cq.Workplane("XY")
        .box(
            params.sleeve_outer_mm,
            params.sleeve_outer_mm,
            params.fan_plate_thickness_mm,
            centered=(True, True, False),
        )
    )
    plate = plate.cut(
        cq.Workplane("XY")
        .circle(params.fan_aperture_mm / 2.0)
        .extrude(params.fan_plate_thickness_mm)
    )
    off = params.fan_hole_spacing_mm / 2.0
    for x in (-off, off):
        for y in (-off, off):
            plate = plate.cut(
                cq.Workplane("XY")
                .center(x, y)
                .circle(params.fan_hole_diameter_mm / 2.0)
                .extrude(params.fan_plate_thickness_mm)
            )
    return plate


def _inner_transition(params: HeatExchangerParameters) -> cq.Workplane:
    """Square at z=0 to round fan opening at z=plenum length."""
    return (
        cq.Workplane("XY")
        .rect(params.sleeve_inner_width_mm, params.sleeve_inner_depth_mm)
        .workplane(offset=params.plenum_length_mm)
        .circle(params.fan_aperture_mm / 2.0)
        .loft(combine=True)
    )


def _positive_plenum(params: HeatExchangerParameters) -> cq.Workplane:
    """Interface at z=0, fan end at positive Z.

    The plenum-side flange has the smaller active-core opening, so after the
    core is slid into the open sleeve and the plenum is bolted on, the flange
    itself becomes the axial cartridge stop and gasket land.
    """

    ft = params.interface_flange_thickness_mm
    pl = params.plenum_length_mm
    overlap = 0.20

    flange = _interface_flange(
        params,
        inner_opening_mm=params.active_core_opening_mm,
    )

    body_z0 = ft - overlap
    body_len = pl + 2.0 * overlap
    body = (
        cq.Workplane("XY")
        .box(
            params.sleeve_outer_mm,
            params.sleeve_outer_mm,
            body_len,
            centered=(True, True, False),
        )
        .translate((0.0, 0.0, body_z0))
    )

    passage = (
        cq.Workplane("XY")
        .workplane(offset=body_z0)
        .rect(params.sleeve_inner_width_mm, params.sleeve_inner_depth_mm)
        .workplane(offset=body_len)
        .circle(params.fan_aperture_mm / 2.0)
        .loft(combine=True)
    )
    body = body.cut(passage)

    plate = _fan_plate(params).translate(
        (0.0, 0.0, ft + pl)
    )

    return flange.union(body).union(plate).clean()


def _add_outside_drain(
    params: HeatExchangerParameters,
    outside_plenum: cq.Workplane,
) -> cq.Workplane:
    """Add a downward drain boss/hole to the outside plenum floor."""

    ft = params.interface_flange_thickness_mm
    # Put drain near the outer/fan end so a 2 degree outward installation
    # slope moves condensate toward it.
    z = ft + 0.78 * params.plenum_length_mm
    y_bottom = -params.sleeve_outer_mm / 2.0

    boss_solid = cq.Solid.makeCylinder(
        params.drain_boss_outer_diameter_mm / 2.0,
        params.drain_boss_length_mm + 1.0,
        cq.Vector(0.0, y_bottom + 1.0, z),
        cq.Vector(0.0, -1.0, 0.0),
    )
    boss = cq.Workplane(obj=boss_solid)

    # Through-hole along Y, deliberately longer than the complete shell.
    cutter_solid = cq.Solid.makeCylinder(
        params.drain_hole_diameter_mm / 2.0,
        params.sleeve_outer_mm + 40.0,
        cq.Vector(0.0, -params.sleeve_outer_mm / 2.0 - 20.0, z),
        cq.Vector(0.0, 1.0, 0.0),
    )
    cutter = cq.Workplane(obj=cutter_solid)

    return outside_plenum.union(boss).cut(cutter).clean()


def build_core_sleeve(params: HeatExchangerParameters) -> cq.Workplane:
    """Open-ended sleeve; core is inserted before attaching a plenum."""

    params.validate()

    outer = (
        cq.Workplane("XY")
        .box(
            params.sleeve_outer_mm,
            params.sleeve_outer_mm,
            params.sleeve_length_mm,
            centered=(True, True, False),
        )
    )
    inner = (
        cq.Workplane("XY")
        .box(
            params.sleeve_inner_width_mm,
            params.sleeve_inner_depth_mm,
            params.sleeve_length_mm,
            centered=(True, True, False),
        )
    )
    body = outer.cut(inner)

    # External clamping flanges at both sleeve ends.
    room_flange = _interface_flange(
        params, inner_opening_mm=params.sleeve_inner_width_mm
    )
    outside_flange = _interface_flange(
        params, inner_opening_mm=params.sleeve_inner_width_mm
    ).translate(
        (0.0, 0.0, params.sleeve_length_mm - params.interface_flange_thickness_mm)
    )

    return body.union(room_flange).union(outside_flange).clean()


def build_room_plenum(params: HeatExchangerParameters) -> cq.Workplane:
    # Build positive then mirror Z so the interface remains at z=0.
    positive = _positive_plenum(params)
    mirrored = positive.mirror("XY")
    return mirrored.clean()


def build_outside_plenum(params: HeatExchangerParameters) -> cq.Workplane:
    positive = _positive_plenum(params)
    positive = _add_outside_drain(params, positive)
    return positive.translate((0.0, 0.0, params.sleeve_length_mm)).clean()


def build_gasket(params: HeatExchangerParameters) -> cq.Workplane:
    """Nominal compressible square gasket placed on the core perimeter frame."""
    return _square_ring(
        params.width_mm,
        params.active_core_opening_mm,
        params.gasket_compressed_thickness_mm,
    )


def positioned_core(params: HeatExchangerParameters) -> cq.Workplane:
    from .core import build_core
    return build_core(params).translate((0.0, 0.0, params.core_start_z_mm))


def positioned_room_gasket(params: HeatExchangerParameters) -> cq.Workplane:
    return build_gasket(params).translate(
        (0.0, 0.0, 0.0)
    )


def positioned_outside_gasket(params: HeatExchangerParameters) -> cq.Workplane:
    return build_gasket(params).translate(
        (
            0.0,
            0.0,
            params.sleeve_length_mm
            - params.gasket_compressed_thickness_mm,
        )
    )


def build_assembly_compound(params: HeatExchangerParameters) -> cq.Workplane:
    shapes = [
        build_core_sleeve(params).val(),
        build_room_plenum(params).val(),
        build_outside_plenum(params).val(),
        positioned_core(params).val(),
        positioned_room_gasket(params).val(),
        positioned_outside_gasket(params).val(),
    ]
    return cq.Workplane(obj=cq.Compound.makeCompound(shapes))
