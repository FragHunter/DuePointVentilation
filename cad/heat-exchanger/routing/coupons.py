from __future__ import annotations

import cadquery as cq

from .parameters import RoutingCouponParameters


def build_linkage_coupon(params: RoutingCouponParameters) -> cq.Workplane:
    """Generic linkage bar that bolts to the supplied servo horn.

    No MZ966 spline geometry is assumed. The center hole is the linkage pivot;
    symmetric radius holes let the real mechanism test several lever arms.
    """
    params.validate()

    body = cq.Workplane("XY").box(
        params.linkage_length_mm,
        params.linkage_width_mm,
        params.linkage_thickness_mm,
        centered=(True, True, False),
    )

    hole_radius = params.linkage_hole_diameter_mm / 2.0
    positions = [0.0]
    for offset in params.linkage_hole_offsets_mm:
        positions.extend((-offset, offset))

    for x in positions:
        cutter = (
            cq.Workplane("XY")
            .center(x, 0.0)
            .circle(hole_radius)
            .extrude(params.linkage_thickness_mm)
        )
        body = body.cut(cutter)

    return body.clean()


def _horizontal_cylinder(
    *,
    x_mm: float,
    diameter_mm: float,
    length_mm: float,
    z_mm: float,
    y_start_mm: float,
) -> cq.Workplane:
    solid = cq.Solid.makeCylinder(
        diameter_mm / 2.0,
        length_mm,
        cq.Vector(x_mm, y_start_mm, z_mm),
        cq.Vector(0.0, 1.0, 0.0),
    )
    return cq.Workplane(obj=solid)


def build_shaft_clearance_coupon(params: RoutingCouponParameters) -> cq.Workplane:
    """Horizontal-hole coupon for choosing a printable flap-shaft bearing clearance.

    Horizontal bores intentionally reproduce the more difficult print orientation
    expected for a damper shaft. The configured diameter series brackets the
    provisional 4 mm shaft choice.
    """
    params.validate()

    body = cq.Workplane("XY").box(
        params.shaft_coupon_length_mm,
        params.shaft_coupon_width_mm,
        params.shaft_coupon_height_mm,
        centered=(True, True, False),
    )

    count = len(params.shaft_bore_diameters_mm)
    x0 = -0.5 * (count - 1) * params.shaft_bore_pitch_mm
    z = params.shaft_coupon_height_mm / 2.0
    y_start = -params.shaft_coupon_width_mm / 2.0 - 1.0
    bore_length = params.shaft_coupon_width_mm + 2.0

    for index, diameter in enumerate(params.shaft_bore_diameters_mm):
        x = x0 + index * params.shaft_bore_pitch_mm
        body = body.cut(
            _horizontal_cylinder(
                x_mm=x,
                diameter_mm=diameter,
                length_mm=bore_length,
                z_mm=z,
                y_start_mm=y_start,
            )
        )

    return body.clean()


def build_seal_gap_coupon(params: RoutingCouponParameters) -> cq.Workplane:
    """Stepped slot gauge for flap-edge/seal clearance selection.

    The slots are open from the top and retain a solid floor. The series is used
    to test the real gasket/seal strip before committing to a full diverter seat.
    """
    params.validate()

    body = cq.Workplane("XY").box(
        params.seal_coupon_length_mm,
        params.seal_coupon_width_mm,
        params.seal_coupon_height_mm,
        centered=(True, True, False),
    )

    count = len(params.seal_slot_widths_mm)
    x0 = -0.5 * (count - 1) * params.seal_slot_pitch_mm
    slot_length_y = params.seal_coupon_width_mm + 2.0
    z0 = params.seal_coupon_height_mm - params.seal_slot_depth_mm

    for index, width in enumerate(params.seal_slot_widths_mm):
        x = x0 + index * params.seal_slot_pitch_mm
        cutter = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .center(x, 0.0)
            .rect(width, slot_length_y)
            .extrude(params.seal_slot_depth_mm + 0.5)
        )
        body = body.cut(cutter)

    return body.clean()
