from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RoutingPrototypeParameters:
    revision: str

    printer_x_mm: float
    printer_y_mm: float
    printer_z_mm: float

    transition_length_mm: float
    transition_wall_mm: float
    transition_outlet_width_mm: float
    transition_outlet_height_mm: float

    collector_width_mm: float
    collector_depth_mm: float
    collector_length_mm: float
    collector_wall_mm: float
    collector_inlet_width_mm: float
    collector_inlet_height_mm: float
    collector_inlet_offset_mm: float
    collector_outlet_width_mm: float
    collector_outlet_height_mm: float
    collector_splitter_height_mm: float

    diverter_width_mm: float
    diverter_depth_mm: float
    diverter_height_mm: float
    diverter_wall_mm: float
    diverter_separator_mm: float
    diverter_common_port_height_mm: float
    diverter_branch_port_height_mm: float
    diverter_branch_gap_mm: float
    diverter_shaft_bore_mm: float
    diverter_flap_clearance_mm: float
    diverter_flap_length_mm: float
    diverter_flap_thickness_mm: float

    material: str
    nozzle_mm: float
    layer_height_mm: float

    @property
    def diverter_chamber_width_mm(self) -> float:
        return (
            self.diverter_width_mm
            - 2.0 * self.diverter_wall_mm
            - self.diverter_separator_mm
        ) / 2.0

    @property
    def diverter_flap_width_mm(self) -> float:
        return self.diverter_chamber_width_mm - 2.0 * self.diverter_flap_clearance_mm

    @property
    def diverter_branch_center_offset_mm(self) -> float:
        return (self.diverter_branch_port_height_mm + self.diverter_branch_gap_mm) / 2.0

    def validate(self) -> None:
        positive = (
            self.printer_x_mm,
            self.printer_y_mm,
            self.printer_z_mm,
            self.transition_length_mm,
            self.transition_wall_mm,
            self.transition_outlet_width_mm,
            self.transition_outlet_height_mm,
            self.collector_width_mm,
            self.collector_depth_mm,
            self.collector_length_mm,
            self.collector_wall_mm,
            self.collector_inlet_width_mm,
            self.collector_inlet_height_mm,
            self.collector_inlet_offset_mm,
            self.collector_outlet_width_mm,
            self.collector_outlet_height_mm,
            self.collector_splitter_height_mm,
            self.diverter_width_mm,
            self.diverter_depth_mm,
            self.diverter_height_mm,
            self.diverter_wall_mm,
            self.diverter_separator_mm,
            self.diverter_common_port_height_mm,
            self.diverter_branch_port_height_mm,
            self.diverter_branch_gap_mm,
            self.diverter_shaft_bore_mm,
            self.diverter_flap_clearance_mm,
            self.diverter_flap_length_mm,
            self.diverter_flap_thickness_mm,
            self.nozzle_mm,
            self.layer_height_mm,
        )
        if any(value <= 0 for value in positive):
            raise ValueError("routing prototype dimensions must be positive")

        for x, y, z, label in (
            (
                max(120.0, self.transition_outlet_width_mm + 2.0 * self.transition_wall_mm),
                max(120.0, self.transition_outlet_height_mm + 2.0 * self.transition_wall_mm),
                self.transition_length_mm + self.transition_wall_mm,
                "fan transition",
            ),
            (
                self.collector_width_mm,
                self.collector_depth_mm,
                self.collector_length_mm,
                "supply collector",
            ),
            (
                self.diverter_width_mm,
                self.diverter_depth_mm,
                self.diverter_height_mm,
                "double diverter",
            ),
        ):
            if x > self.printer_x_mm or y > self.printer_y_mm or z > self.printer_z_mm:
                raise ValueError(f"{label} exceeds configured printer envelope")

        if self.collector_inlet_width_mm >= self.collector_width_mm:
            raise ValueError("collector inlet width must fit collector")
        if 2.0 * (
            self.collector_inlet_offset_mm + self.collector_inlet_height_mm / 2.0
        ) > self.collector_depth_mm - 2.0 * self.collector_wall_mm:
            raise ValueError("collector inlet pair does not fit inside inner depth")
        if self.collector_outlet_width_mm > self.collector_width_mm - 2.0 * self.collector_wall_mm:
            raise ValueError("collector outlet width exceeds inner width")
        if self.collector_outlet_height_mm > self.collector_depth_mm - 2.0 * self.collector_wall_mm:
            raise ValueError("collector outlet height exceeds inner depth")
        if self.collector_splitter_height_mm >= self.collector_length_mm - 2.0 * self.collector_wall_mm:
            raise ValueError("collector splitter must terminate before outlet")

        if self.diverter_chamber_width_mm <= 0:
            raise ValueError("diverter walls leave no chamber width")
        if self.diverter_common_port_height_mm >= self.diverter_height_mm - 2.0 * self.diverter_wall_mm:
            raise ValueError("diverter common port is too tall")
        branch_total = (
            2.0 * self.diverter_branch_port_height_mm
            + self.diverter_branch_gap_mm
        )
        if branch_total >= self.diverter_height_mm - 2.0 * self.diverter_wall_mm:
            raise ValueError("diverter branch ports do not fit")
        if self.diverter_flap_width_mm <= 0:
            raise ValueError("diverter flap clearance leaves no flap width")
        if self.diverter_flap_length_mm >= self.diverter_height_mm - 2.0 * self.diverter_wall_mm:
            raise ValueError("diverter flap is too long for chamber")
        if self.diverter_shaft_bore_mm >= self.diverter_flap_length_mm:
            raise ValueError("diverter shaft bore must fit flap")


def _required(mapping: dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise ValueError(f"missing routing prototype key: {key}")
    return mapping[key]


def load_routing_prototype_parameters(path: str | Path) -> RoutingPrototypeParameters:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    printer = _required(data, "printer")
    transition = _required(data, "fan_transition")
    collector = _required(data, "supply_collector")
    diverter = _required(data, "double_diverter")
    printing = _required(data, "printing")

    params = RoutingPrototypeParameters(
        revision=str(_required(data, "revision")),
        printer_x_mm=float(_required(printer, "x_mm")),
        printer_y_mm=float(_required(printer, "y_mm")),
        printer_z_mm=float(_required(printer, "z_mm")),
        transition_length_mm=float(_required(transition, "length_mm")),
        transition_wall_mm=float(_required(transition, "wall_mm")),
        transition_outlet_width_mm=float(_required(transition, "outlet_width_mm")),
        transition_outlet_height_mm=float(_required(transition, "outlet_height_mm")),
        collector_width_mm=float(_required(collector, "width_mm")),
        collector_depth_mm=float(_required(collector, "depth_mm")),
        collector_length_mm=float(_required(collector, "length_mm")),
        collector_wall_mm=float(_required(collector, "wall_mm")),
        collector_inlet_width_mm=float(_required(collector, "inlet_width_mm")),
        collector_inlet_height_mm=float(_required(collector, "inlet_height_mm")),
        collector_inlet_offset_mm=float(_required(collector, "inlet_offset_mm")),
        collector_outlet_width_mm=float(_required(collector, "outlet_width_mm")),
        collector_outlet_height_mm=float(_required(collector, "outlet_height_mm")),
        collector_splitter_height_mm=float(_required(collector, "splitter_height_mm")),
        diverter_width_mm=float(_required(diverter, "width_mm")),
        diverter_depth_mm=float(_required(diverter, "depth_mm")),
        diverter_height_mm=float(_required(diverter, "height_mm")),
        diverter_wall_mm=float(_required(diverter, "wall_mm")),
        diverter_separator_mm=float(_required(diverter, "separator_mm")),
        diverter_common_port_height_mm=float(_required(diverter, "common_port_height_mm")),
        diverter_branch_port_height_mm=float(_required(diverter, "branch_port_height_mm")),
        diverter_branch_gap_mm=float(_required(diverter, "branch_gap_mm")),
        diverter_shaft_bore_mm=float(_required(diverter, "shaft_bore_mm")),
        diverter_flap_clearance_mm=float(_required(diverter, "flap_clearance_mm")),
        diverter_flap_length_mm=float(_required(diverter, "flap_length_mm")),
        diverter_flap_thickness_mm=float(_required(diverter, "flap_thickness_mm")),
        material=str(_required(printing, "material")),
        nozzle_mm=float(_required(printing, "nozzle_mm")),
        layer_height_mm=float(_required(printing, "layer_height_mm")),
    )
    params.validate()
    return params
