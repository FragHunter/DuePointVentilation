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
    channel_count: int
    channel_height_mm: float
    plate_thickness_mm: float
    rail_thickness_mm: float
    fan_nominal_mm: float
    duct_nominal_mm: float
    material: str
    nozzle_mm: float
    layer_height_mm: float
    removable_core: bool
    condensate_drain_required: bool
    reserve_bypass: bool

    @property
    def plate_count(self) -> int:
        return self.channel_count + 1

    @property
    def total_height_mm(self) -> float:
        return (
            self.plate_count * self.plate_thickness_mm
            + self.channel_count * self.channel_height_mm
        )

    @property
    def x_flow_channels(self) -> int:
        return (self.channel_count + 1) // 2

    @property
    def y_flow_channels(self) -> int:
        return self.channel_count // 2

    @property
    def x_flow_open_area_mm2(self) -> float:
        useful_width = self.depth_mm - 2.0 * self.rail_thickness_mm
        return self.x_flow_channels * useful_width * self.channel_height_mm

    @property
    def y_flow_open_area_mm2(self) -> float:
        useful_width = self.width_mm - 2.0 * self.rail_thickness_mm
        return self.y_flow_channels * useful_width * self.channel_height_mm

    @property
    def gross_transfer_area_m2(self) -> float:
        # Approximate two-sided channel contact area. This is intentionally a
        # gross geometric metric, not a prediction of thermal effectiveness.
        return (
            2.0
            * self.channel_count
            * self.width_mm
            * self.depth_mm
            / 1_000_000.0
        )

    def validate(self) -> None:
        if self.topology != "cross_flow_plate_stack":
            raise ValueError(f"Unsupported topology: {self.topology}")
        if self.width_mm <= 0 or self.depth_mm <= 0:
            raise ValueError("Core width/depth must be positive")
        if self.channel_count < 2:
            raise ValueError("At least two channels are required")
        if self.channel_height_mm <= 0:
            raise ValueError("Channel height must be positive")
        if self.plate_thickness_mm <= 0:
            raise ValueError("Plate thickness must be positive")
        if self.rail_thickness_mm <= 0:
            raise ValueError("Rail thickness must be positive")
        if 2.0 * self.rail_thickness_mm >= min(self.width_mm, self.depth_mm):
            raise ValueError("Rails consume the entire flow opening")
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
    printing = _require(data, "printing")
    design = _require(data, "design")

    params = HeatExchangerParameters(
        revision=str(_require(data, "revision")),
        topology=str(_require(data, "topology")),
        width_mm=float(_require(core, "width_mm")),
        depth_mm=float(_require(core, "depth_mm")),
        channel_count=int(_require(core, "channel_count")),
        channel_height_mm=float(_require(core, "channel_height_mm")),
        plate_thickness_mm=float(_require(core, "plate_thickness_mm")),
        rail_thickness_mm=float(_require(core, "rail_thickness_mm")),
        fan_nominal_mm=float(_require(interfaces, "fan_nominal_mm")),
        duct_nominal_mm=float(_require(interfaces, "duct_nominal_mm")),
        material=str(_require(printing, "material")),
        nozzle_mm=float(_require(printing, "nozzle_mm")),
        layer_height_mm=float(_require(printing, "layer_height_mm")),
        removable_core=bool(_require(design, "removable_core")),
        condensate_drain_required=bool(
            _require(design, "condensate_drain_required")
        ),
        reserve_bypass=bool(_require(design, "reserve_bypass")),
    )
    params.validate()
    return params
