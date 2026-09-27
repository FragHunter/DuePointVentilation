from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RoutingCouponParameters:
    revision: str
    printer_x_mm: float
    printer_y_mm: float
    printer_z_mm: float

    linkage_length_mm: float
    linkage_width_mm: float
    linkage_thickness_mm: float
    linkage_hole_diameter_mm: float
    linkage_hole_offsets_mm: tuple[float, ...]

    shaft_coupon_length_mm: float
    shaft_coupon_width_mm: float
    shaft_coupon_height_mm: float
    shaft_bore_diameters_mm: tuple[float, ...]
    shaft_bore_pitch_mm: float

    seal_coupon_length_mm: float
    seal_coupon_width_mm: float
    seal_coupon_height_mm: float
    seal_slot_widths_mm: tuple[float, ...]
    seal_slot_pitch_mm: float
    seal_slot_depth_mm: float

    material: str
    nozzle_mm: float
    layer_height_mm: float

    def validate(self) -> None:
        positive = (
            self.printer_x_mm,
            self.printer_y_mm,
            self.printer_z_mm,
            self.linkage_length_mm,
            self.linkage_width_mm,
            self.linkage_thickness_mm,
            self.linkage_hole_diameter_mm,
            self.shaft_coupon_length_mm,
            self.shaft_coupon_width_mm,
            self.shaft_coupon_height_mm,
            self.shaft_bore_pitch_mm,
            self.seal_coupon_length_mm,
            self.seal_coupon_width_mm,
            self.seal_coupon_height_mm,
            self.seal_slot_pitch_mm,
            self.seal_slot_depth_mm,
            self.nozzle_mm,
            self.layer_height_mm,
        )
        if any(value <= 0 for value in positive):
            raise ValueError("routing coupon dimensions must be positive")

        if not self.linkage_hole_offsets_mm:
            raise ValueError("at least one linkage hole offset is required")
        if not self.shaft_bore_diameters_mm:
            raise ValueError("at least one shaft bore diameter is required")
        if not self.seal_slot_widths_mm:
            raise ValueError("at least one seal slot width is required")

        if any(offset <= 0 for offset in self.linkage_hole_offsets_mm):
            raise ValueError("linkage hole offsets must be positive")
        if max(self.linkage_hole_offsets_mm) >= self.linkage_length_mm / 2.0:
            raise ValueError("linkage holes must fit inside the coupon")

        if any(d <= 0 for d in self.shaft_bore_diameters_mm):
            raise ValueError("shaft bore diameters must be positive")
        required_shaft_length = (
            (len(self.shaft_bore_diameters_mm) - 1) * self.shaft_bore_pitch_mm
            + 2.0 * self.shaft_bore_pitch_mm
        )
        if required_shaft_length > self.shaft_coupon_length_mm:
            raise ValueError("shaft coupon is too short for configured bore series")
        if max(self.shaft_bore_diameters_mm) >= self.shaft_coupon_height_mm:
            raise ValueError("shaft bore must fit inside coupon height")

        if any(width <= 0 for width in self.seal_slot_widths_mm):
            raise ValueError("seal slot widths must be positive")
        required_seal_length = (
            (len(self.seal_slot_widths_mm) - 1) * self.seal_slot_pitch_mm
            + 2.0 * self.seal_slot_pitch_mm
        )
        if required_seal_length > self.seal_coupon_length_mm:
            raise ValueError("seal coupon is too short for configured slot series")
        if self.seal_slot_depth_mm >= self.seal_coupon_height_mm:
            raise ValueError("seal slot depth must leave a floor")

        for x, y, z, label in (
            (self.linkage_length_mm, self.linkage_width_mm, self.linkage_thickness_mm, "linkage"),
            (self.shaft_coupon_length_mm, self.shaft_coupon_width_mm, self.shaft_coupon_height_mm, "shaft"),
            (self.seal_coupon_length_mm, self.seal_coupon_width_mm, self.seal_coupon_height_mm, "seal"),
        ):
            if x > self.printer_x_mm or y > self.printer_y_mm or z > self.printer_z_mm:
                raise ValueError(f"{label} coupon exceeds configured printer envelope")


def _required(mapping: dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise ValueError(f"missing routing configuration key: {key}")
    return mapping[key]


def load_routing_parameters(path: str | Path) -> RoutingCouponParameters:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    printer = _required(data, "printer")
    linkage = _required(data, "linkage_coupon")
    shaft = _required(data, "shaft_clearance_coupon")
    seal = _required(data, "seal_gap_coupon")
    printing = _required(data, "printing")

    params = RoutingCouponParameters(
        revision=str(_required(data, "revision")),
        printer_x_mm=float(_required(printer, "x_mm")),
        printer_y_mm=float(_required(printer, "y_mm")),
        printer_z_mm=float(_required(printer, "z_mm")),
        linkage_length_mm=float(_required(linkage, "length_mm")),
        linkage_width_mm=float(_required(linkage, "width_mm")),
        linkage_thickness_mm=float(_required(linkage, "thickness_mm")),
        linkage_hole_diameter_mm=float(_required(linkage, "hole_diameter_mm")),
        linkage_hole_offsets_mm=tuple(float(v) for v in _required(linkage, "hole_offsets_mm")),
        shaft_coupon_length_mm=float(_required(shaft, "length_mm")),
        shaft_coupon_width_mm=float(_required(shaft, "width_mm")),
        shaft_coupon_height_mm=float(_required(shaft, "height_mm")),
        shaft_bore_diameters_mm=tuple(float(v) for v in _required(shaft, "bore_diameters_mm")),
        shaft_bore_pitch_mm=float(_required(shaft, "bore_pitch_mm")),
        seal_coupon_length_mm=float(_required(seal, "length_mm")),
        seal_coupon_width_mm=float(_required(seal, "width_mm")),
        seal_coupon_height_mm=float(_required(seal, "height_mm")),
        seal_slot_widths_mm=tuple(float(v) for v in _required(seal, "slot_widths_mm")),
        seal_slot_pitch_mm=float(_required(seal, "slot_pitch_mm")),
        seal_slot_depth_mm=float(_required(seal, "slot_depth_mm")),
        material=str(_required(printing, "material")),
        nozzle_mm=float(_required(printing, "nozzle_mm")),
        layer_height_mm=float(_required(printing, "layer_height_mm")),
    )
    params.validate()
    return params
