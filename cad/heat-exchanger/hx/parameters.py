from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class HeatExchangerParameters:
    revision: str
    topology: str
    width_mm: float
    depth_mm: float
    length_mm: float
    cells_x: int
    cells_y: int
    wall_thickness_mm: float
    fan_nominal_mm: float
    duct_nominal_mm: float
    phase_time_s: float
    switch_deadtime_s: float
    routing_variant: str
    core_clearance_mm: float
    shell_wall_mm: float
    plenum_length_mm: float
    fan_plate_thickness_mm: float
    fan_aperture_mm: float
    fan_hole_spacing_mm: float
    fan_hole_diameter_mm: float
    material: str
    nozzle_mm: float
    layer_height_mm: float
    removable_core: bool
    condensate_drain_required: bool
    reserve_bypass: bool
    paired_modules: int

    @property
    def channel_width_mm(self) -> float:
        return (
            self.width_mm - (self.cells_x + 1) * self.wall_thickness_mm
        ) / self.cells_x

    @property
    def channel_depth_mm(self) -> float:
        return (
            self.depth_mm - (self.cells_y + 1) * self.wall_thickness_mm
        ) / self.cells_y

    @property
    def channel_count(self) -> int:
        return self.cells_x * self.cells_y

    @property
    def open_area_mm2(self) -> float:
        return (
            self.channel_count
            * self.channel_width_mm
            * self.channel_depth_mm
        )

    @property
    def frontal_area_mm2(self) -> float:
        return self.width_mm * self.depth_mm

    @property
    def open_area_ratio(self) -> float:
        return self.open_area_mm2 / self.frontal_area_mm2

    @property
    def gross_internal_surface_area_m2(self) -> float:
        perimeter_mm = 2.0 * (
            self.channel_width_mm + self.channel_depth_mm
        )
        return (
            self.channel_count
            * perimeter_mm
            * self.length_mm
            / 1_000_000.0
        )

    @property
    def approximate_solid_volume_cm3(self) -> float:
        gross_mm3 = self.width_mm * self.depth_mm * self.length_mm
        open_mm3 = self.open_area_mm2 * self.length_mm
        return (gross_mm3 - open_mm3) / 1000.0

    @property
    def module_passage_width_mm(self) -> float:
        return self.width_mm + self.core_clearance_mm

    @property
    def module_passage_depth_mm(self) -> float:
        return self.depth_mm + self.core_clearance_mm

    @property
    def module_outer_mm(self) -> float:
        return max(
            self.module_passage_width_mm + 2.0 * self.shell_wall_mm,
            self.module_passage_depth_mm + 2.0 * self.shell_wall_mm,
            self.fan_nominal_mm + 8.0,
        )

    @property
    def module_body_length_mm(self) -> float:
        return self.length_mm + 2.0 * self.plenum_length_mm

    @property
    def module_total_length_mm(self) -> float:
        return self.module_body_length_mm + 2.0 * self.fan_plate_thickness_mm

    def validate(self) -> None:
        if self.topology != "regenerative_matrix":
            raise ValueError(f"Unsupported topology: {self.topology}")
        if self.width_mm <= 0 or self.depth_mm <= 0 or self.length_mm <= 0:
            raise ValueError("Core dimensions must be positive")
        if self.cells_x < 1 or self.cells_y < 1:
            raise ValueError("At least one channel is required in each axis")
        if self.wall_thickness_mm <= 0:
            raise ValueError("Wall thickness must be positive")
        if self.channel_width_mm <= 0 or self.channel_depth_mm <= 0:
            raise ValueError("Wall/cell geometry leaves no open airflow channel")
        if self.phase_time_s <= 0:
            raise ValueError("Pendulum phase time must be positive")
        if self.switch_deadtime_s < 0:
            raise ValueError("Switch dead-time cannot be negative")
        if self.paired_modules != 2:
            raise ValueError("HX-V1 currently models exactly two paired modules")
        if self.routing_variant != "axial_opposed_fans":
            raise ValueError(f"Unsupported routing variant: {self.routing_variant}")
        if self.core_clearance_mm <= 0 or self.shell_wall_mm <= 0:
            raise ValueError("Module clearance/wall dimensions must be positive")
        if self.plenum_length_mm < 0 or self.fan_plate_thickness_mm <= 0:
            raise ValueError("Module length dimensions are invalid")
        if not 0 < self.fan_aperture_mm < self.module_outer_mm:
            raise ValueError("Fan aperture must fit inside the module")
        if self.fan_hole_spacing_mm <= 0 or self.fan_hole_diameter_mm <= 0:
            raise ValueError("Fan mount dimensions must be positive")
        if self.nozzle_mm <= 0 or self.layer_height_mm <= 0:
            raise ValueError("Print dimensions must be positive")


def _require(mapping: dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise ValueError(f"Missing configuration key: {key}")
    return mapping[key]


def load_parameters(path: str | Path) -> HeatExchangerParameters:
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    core = _require(data, "core")
    interfaces = _require(data, "interfaces")
    operation = _require(data, "operation")
    module = _require(data, "module")
    printing = _require(data, "printing")
    design = _require(data, "design")

    params = HeatExchangerParameters(
        revision=str(_require(data, "revision")),
        topology=str(_require(data, "topology")),
        width_mm=float(_require(core, "width_mm")),
        depth_mm=float(_require(core, "depth_mm")),
        length_mm=float(_require(core, "length_mm")),
        cells_x=int(_require(core, "cells_x")),
        cells_y=int(_require(core, "cells_y")),
        wall_thickness_mm=float(_require(core, "wall_thickness_mm")),
        fan_nominal_mm=float(_require(interfaces, "fan_nominal_mm")),
        duct_nominal_mm=float(_require(interfaces, "duct_nominal_mm")),
        phase_time_s=float(_require(operation, "phase_time_s")),
        switch_deadtime_s=float(_require(operation, "switch_deadtime_s")),
        routing_variant=str(_require(module, "routing_variant")),
        core_clearance_mm=float(_require(module, "core_clearance_mm")),
        shell_wall_mm=float(_require(module, "shell_wall_mm")),
        plenum_length_mm=float(_require(module, "plenum_length_mm")),
        fan_plate_thickness_mm=float(
            _require(module, "fan_plate_thickness_mm")
        ),
        fan_aperture_mm=float(_require(module, "fan_aperture_mm")),
        fan_hole_spacing_mm=float(_require(module, "fan_hole_spacing_mm")),
        fan_hole_diameter_mm=float(_require(module, "fan_hole_diameter_mm")),
        material=str(_require(printing, "material")),
        nozzle_mm=float(_require(printing, "nozzle_mm")),
        layer_height_mm=float(_require(printing, "layer_height_mm")),
        removable_core=bool(_require(design, "removable_core")),
        condensate_drain_required=bool(
            _require(design, "condensate_drain_required")
        ),
        reserve_bypass=bool(_require(design, "reserve_bypass")),
        paired_modules=int(_require(design, "paired_modules")),
    )
    params.validate()
    return params
