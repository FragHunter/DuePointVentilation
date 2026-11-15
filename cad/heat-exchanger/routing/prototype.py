from __future__ import annotations

import cadquery as cq

from hx.parameters import HeatExchangerParameters

from .prototype_parameters import RoutingPrototypeParameters


def _box_through_y(
    *,
    width_x_mm: float,
    height_z_mm: float,
    depth_y_mm: float,
    center_x_mm: float,
    center_z_mm: float,
    y_start_mm: float,
) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .center(center_x_mm, center_z_mm)
        .rect(width_x_mm, height_z_mm)
        .extrude(depth_y_mm)
        .translate((0.0, y_start_mm, 0.0))
    )


def build_fan_rect_transition(
    params: RoutingPrototypeParameters,
    hx_params: HeatExchangerParameters,
) -> cq.Workplane:
    """P12 round-aperture to compact rectangular supply-collector transition.

    The P12 interface uses the already modelled project fan aperture and bolt
    pattern. The rectangular outlet is intentionally provisional and is a
    modular interface for ROUTING-V0.2 rather than final duct geometry.
    """

    params.validate()
    hx_params.validate()

    flange_t = params.transition_wall_mm
    length = params.transition_length_mm
    overlap = 0.2

    flange = (
        cq.Workplane("XY")
        .box(
            hx_params.fan_nominal_mm,
            hx_params.fan_nominal_mm,
            flange_t,
            centered=(True, True, False),
        )
        .cut(
            cq.Workplane("XY")
            .circle(hx_params.fan_aperture_mm / 2.0)
            .extrude(flange_t)
        )
    )

    off = hx_params.fan_hole_spacing_mm / 2.0
    for x in (-off, off):
        for y in (-off, off):
            flange = flange.cut(
                cq.Workplane("XY")
                .center(x, y)
                .circle(hx_params.fan_hole_diameter_mm / 2.0)
                .extrude(flange_t)
            )

    outer = (
        cq.Workplane("XY")
        .workplane(offset=flange_t - overlap)
        .rect(hx_params.fan_nominal_mm, hx_params.fan_nominal_mm)
        .workplane(offset=length + overlap)
        .rect(
            params.transition_outlet_width_mm + 2.0 * params.transition_wall_mm,
            params.transition_outlet_height_mm + 2.0 * params.transition_wall_mm,
        )
        .loft(combine=True, ruled=True)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=flange_t - overlap)
        .circle(hx_params.fan_aperture_mm / 2.0)
        .workplane(offset=length + 2.0 * overlap)
        .rect(
            params.transition_outlet_width_mm,
            params.transition_outlet_height_mm,
        )
        .loft(combine=True, ruled=True)
    )

    return flange.union(outer.cut(inner)).clean()


def build_supply_merge_collector(
    params: RoutingPrototypeParameters,
) -> cq.Workplane:
    """Compact two-inlet supply plenum with a common square outlet.

    This is a plenum-style merge prototype, not a final low-loss Y-collector.
    A short center splitter reduces direct inlet-to-inlet interaction and ends
    before the common outlet so both P12 supply branches share one pressure
    chamber.
    """

    params.validate()

    w = params.collector_width_mm
    d = params.collector_depth_mm
    length = params.collector_length_mm
    wall = params.collector_wall_mm

    outer = cq.Workplane("XY").box(w, d, length, centered=(True, True, False))
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .box(
            w - 2.0 * wall,
            d - 2.0 * wall,
            length - 2.0 * wall,
            centered=(True, True, False),
        )
    )
    body = outer.cut(cavity)

    for y in (-params.collector_inlet_offset_mm, params.collector_inlet_offset_mm):
        inlet = (
            cq.Workplane("XY")
            .center(0.0, y)
            .rect(
                params.collector_inlet_width_mm,
                params.collector_inlet_height_mm,
            )
            .extrude(wall + 1.0)
        )
        body = body.cut(inlet)

    outlet = (
        cq.Workplane("XY")
        .workplane(offset=length - wall - 1.0)
        .rect(
            params.collector_outlet_width_mm,
            params.collector_outlet_height_mm,
        )
        .extrude(wall + 2.0)
    )
    body = body.cut(outlet)

    splitter = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .box(
            w - 2.0 * wall,
            wall,
            params.collector_splitter_height_mm,
            centered=(True, True, False),
        )
    )
    return body.union(splitter).clean()


def build_double_diverter_body(
    params: RoutingPrototypeParameters,
) -> cq.Workplane:
    """Two isolated three-way chambers sharing one transverse shaft bore.

    Left and right chambers remain separated by a structural center wall.
    Each chamber has one large common port on the front face and two branch
    ports on the rear face. The common shaft bore is only a geometry proof;
    final bearings, seals, hard stops and servo coupling depend on bench data.
    """

    params.validate()

    width = params.diverter_width_mm
    depth = params.diverter_depth_mm
    height = params.diverter_height_mm
    wall = params.diverter_wall_mm
    separator = params.diverter_separator_mm
    chamber = params.diverter_chamber_width_mm

    body = cq.Workplane("XY").box(
        width,
        depth,
        height,
        centered=(True, True, True),
    )

    chamber_center = separator / 2.0 + chamber / 2.0
    cavity_depth = depth - 2.0 * wall
    cavity_height = height - 2.0 * wall

    for x in (-chamber_center, chamber_center):
        cavity = (
            cq.Workplane("XY")
            .box(
                chamber,
                cavity_depth,
                cavity_height,
                centered=(True, True, True),
            )
            .translate((x, 0.0, 0.0))
        )
        body = body.cut(cavity)

        common_port = _box_through_y(
            width_x_mm=chamber - 2.0,
            height_z_mm=params.diverter_common_port_height_mm,
            depth_y_mm=wall + 2.0,
            center_x_mm=x,
            center_z_mm=0.0,
            y_start_mm=-depth / 2.0 - 1.0,
        )
        body = body.cut(common_port)

        zoff = params.diverter_branch_center_offset_mm
        for z in (-zoff, zoff):
            branch_port = _box_through_y(
                width_x_mm=chamber - 2.0,
                height_z_mm=params.diverter_branch_port_height_mm,
                depth_y_mm=wall + 2.0,
                center_x_mm=x,
                center_z_mm=z,
                y_start_mm=depth / 2.0 - wall - 1.0,
            )
            body = body.cut(branch_port)

    shaft = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            params.diverter_shaft_bore_mm / 2.0,
            width + 2.0,
            cq.Vector(-width / 2.0 - 1.0, 0.0, 0.0),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    return body.cut(shaft).clean()


def build_diverter_flap_blank(
    params: RoutingPrototypeParameters,
) -> cq.Workplane:
    """One printable flap blank for the common-shaft diverter prototype."""

    params.validate()

    flap = cq.Workplane("XZ").box(
        params.diverter_flap_width_mm,
        params.diverter_flap_length_mm,
        params.diverter_flap_thickness_mm,
        centered=(True, True, True),
    )

    bore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            params.diverter_shaft_bore_mm / 2.0,
            params.diverter_flap_width_mm + 2.0,
            cq.Vector(-params.diverter_flap_width_mm / 2.0 - 1.0, 0.0, 0.0),
            cq.Vector(1.0, 0.0, 0.0),
        )
    )
    return flap.cut(bore).clean()
