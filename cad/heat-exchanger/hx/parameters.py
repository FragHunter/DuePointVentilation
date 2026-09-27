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
    perimeter_frame_mm: float

    fan_nominal_mm: float
    duct_nominal_mm: float

    phase_time_s: float
    switch_deadtime_s: float

    routing_variant: str
    side_clearance_mm: float
    sleeve_wall_mm: float
    sleeve_length_mm: float
    plenum_length_mm: float
    interface_flange_outer_mm: float
    interface_flange_thickness_mm: float
    interface_hole_spacing_mm: float
    interface_hole_diameter_mm: float
    gasket_nominal_thickness_mm: float
    gasket_compressed_thickness_mm: float
    fan_plate_thickness_mm: float
    fan_aperture_mm: float
    fan_hole_spacing_mm: float
    fan_hole_diameter_mm: float
    drain_hole_diameter_mm: float
    drain_boss_outer_diameter_mm: float
    drain_boss_length_mm: float
    installation_slope_deg: float

    material: str
    nozzle_mm: float
    layer_height_mm: float

    removable_core: bool
    condensate_drain_required: bool
    reserve_bypass: bool
    paired_modules: int

    @property
    def matrix_inner_width_mm(self) -> float:
        return self.width_mm - 2.0 * self.perimeter_frame_mm

    @property
    def matrix_inner_depth_mm(self) -> float:
        return self.depth_mm - 2.0 * self.perimeter_frame_mm

    @property
    def channel_width_mm(self) -> float:
        return (
            self.matrix_inner_width_mm
            - (self.cells_x - 1) * self.wall_thickness_mm
        ) / self.cells_x

    @property
    def channel_depth_mm(self) -> float:
        return (
            self.matrix_inner_depth_mm
            - (self.cells_y - 1) * self.wall_thickness_mm
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
    def hydraulic_diameter_mm(self) -> float:
        a = self.channel_width_mm
        b = self.channel_depth_mm
        return 2.0 * a * b / (a + b)

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
    def sleeve_inner_width_mm(self) -> float:
        return self.width_mm + 2.0 * self.side_clearance_mm

    @property
    def sleeve_inner_depth_mm(self) -> float:
        return self.depth_mm + 2.0 * self.side_clearance_mm

    @property
    def sleeve_outer_mm(self) -> float:
        return max(
            self.sleeve_inner_width_mm + 2.0 * self.sleeve_wall_mm,
            self.sleeve_inner_depth_mm + 2.0 * self.sleeve_wall_mm,
        )

    @property
    def active_core_opening_mm(self) -> float:
        return min(self.matrix_inner_width_mm, self.matrix_inner_depth_mm)

    @property
    def core_start_z_mm(self) -> float:
        return self.gasket_compressed_thickness_mm

    @property
    def core_end_z_mm(self) -> float:
        return self.core_start_z_mm + self.length_mm

    @property
    def plenum_component_length_mm(self) -> float:
        return (
            self.interface_flange_thickness_mm
            + self.plenum_length_mm
            + self.fan_plate_thickness_mm
        )

    @property
    def module_total_length_mm(self) -> float:
        return self.sleeve_length_mm + 2.0 * self.plenum_component_length_mm

    @property
    def fan_aperture_area_mm2(self) -> float:
        import math
        return math.pi * (self.fan_aperture_mm / 2.0) ** 2

    def validate(self) -> None:
        if self.topology != "regenerative_matrix":
            raise ValueError(f"Unsupported topology: {self.topology}")
        if self.width_mm <= 0 or self.depth_mm <= 0 or self.length_mm <= 0:
            raise ValueError("Core dimensions must be positive")
        if self.cells_x < 1 or self.cells_y < 1:
            raise ValueError("At least one channel is required in each axis")
        if self.wall_thickness_mm <= 0 or self.perimeter_frame_mm <= 0:
            raise ValueError("Core wall/frame dimensions must be positive")
        if self.channel_width_mm <= 0 or self.channel_depth_mm <= 0:
            raise ValueError("Wall/cell geometry leaves no open airflow channel")
        if self.perimeter_frame_mm < 2.0 * self.wall_thickness_mm:
            raise ValueError("Perimeter frame should be at least two wall thicknesses")
        if self.phase_time_s <= 0 or self.switch_deadtime_s < 0:
            raise ValueError("Pendulum timing is invalid")
        if self.paired_modules != 2:
            raise ValueError("Current architecture models exactly two paired modules")
        if self.routing_variant != "axial_opposed_fans":
            raise ValueError(f"Unsupported routing variant: {self.routing_variant}")

        positives = [
            self.side_clearance_mm,
            self.sleeve_wall_mm,
            self.sleeve_length_mm,
            self.plenum_length_mm,
            self.interface_flange_outer_mm,
            self.interface_flange_thickness_mm,
            self.interface_hole_spacing_mm,
            self.interface_hole_diameter_mm,
            self.gasket_nominal_thickness_mm,
            self.gasket_compressed_thickness_mm,
            self.fan_plate_thickness_mm,
            self.fan_aperture_mm,
            self.fan_hole_spacing_mm,
            self.fan_hole_diameter_mm,
            self.drain_hole_diameter_mm,
            self.drain_boss_outer_diameter_mm,
            self.drain_boss_length_mm,
            self.nozzle_mm,
            self.layer_height_mm,
        ]
        if any(v <= 0 for v in positives):
            raise ValueError("Module/print dimensions must be positive")

        expected_sleeve = (
            self.length_mm + 2.0 * self.gasket_compressed_thickness_mm
        )
        if abs(self.sleeve_length_mm - expected_sleeve) > 1e-6:
            raise ValueError(
                "Sleeve length must equal core length + two retainer/gasket stacks"
            )
        if self.gasket_compressed_thickness_mm >= self.gasket_nominal_thickness_mm:
            raise ValueError("Compressed gasket thickness must be less than nominal")
        if self.interface_flange_outer_mm <= self.sleeve_outer_mm:
            raise ValueError("Interface flange must extend beyond the sleeve")
        if self.interface_hole_spacing_mm >= self.interface_flange_outer_mm:
            raise ValueError("Interface holes do not fit on flange")
        if self.fan_aperture_mm >= self.sleeve_outer_mm:
            raise ValueError("Fan aperture must fit inside module outer body")
        if self.drain_boss_outer_diameter_mm <= self.drain_hole_diameter_mm:
            raise ValueError("Drain boss must be larger than drain hole")
        if not 0.0 <= self.installation_slope_deg <= 10.0:
            raise ValueError("Installation slope is outside supported range")
        # Make core wall thickness printable as an integer multiple of half-nozzle.
        line_unit = self.nozzle_mm / 2.0
        multiple = self.wall_thickness_mm / line_unit
        if abs(multiple - round(multiple)) > 1e-6:
            raise ValueError(
                "Core wall thickness should align with half-nozzle increments"
            )


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
        perimeter_frame_mm=float(_require(core, "perimeter_frame_mm")),
        fan_nominal_mm=float(_require(interfaces, "fan_nominal_mm")),
        duct_nominal_mm=float(_require(interfaces, "duct_nominal_mm")),
        phase_time_s=float(_require(operation, "phase_time_s")),
        switch_deadtime_s=float(_require(operation, "switch_deadtime_s")),
        routing_variant=str(_require(module, "routing_variant")),
        side_clearance_mm=float(_require(module, "side_clearance_mm")),
        sleeve_wall_mm=float(_require(module, "sleeve_wall_mm")),
        sleeve_length_mm=float(_require(module, "sleeve_length_mm")),
        plenum_length_mm=float(_require(module, "plenum_length_mm")),
        interface_flange_outer_mm=float(
            _require(module, "interface_flange_outer_mm")
        ),
        interface_flange_thickness_mm=float(
            _require(module, "interface_flange_thickness_mm")
        ),
        interface_hole_spacing_mm=float(
            _require(module, "interface_hole_spacing_mm")
        ),
        interface_hole_diameter_mm=float(
            _require(module, "interface_hole_diameter_mm")
        ),
        gasket_nominal_thickness_mm=float(
            _require(module, "gasket_nominal_thickness_mm")
        ),
        gasket_compressed_thickness_mm=float(
            _require(module, "gasket_compressed_thickness_mm")
        ),
        fan_plate_thickness_mm=float(
            _require(module, "fan_plate_thickness_mm")
        ),
        fan_aperture_mm=float(_require(module, "fan_aperture_mm")),
        fan_hole_spacing_mm=float(_require(module, "fan_hole_spacing_mm")),
        fan_hole_diameter_mm=float(_require(module, "fan_hole_diameter_mm")),
        drain_hole_diameter_mm=float(
            _require(module, "drain_hole_diameter_mm")
        ),
        drain_boss_outer_diameter_mm=float(
            _require(module, "drain_boss_outer_diameter_mm")
        ),
        drain_boss_length_mm=float(_require(module, "drain_boss_length_mm")),
        installation_slope_deg=float(
            _require(module, "installation_slope_deg")
        ),
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
