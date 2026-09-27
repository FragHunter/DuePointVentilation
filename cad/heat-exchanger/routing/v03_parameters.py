from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RoutingV03Parameters:
    revision: str

    printer_x_mm: float
    printer_y_mm: float
    printer_z_mm: float

    diverter_outer_mm: float
    diverter_wall_mm: float
    diverter_port_mm: float
    diverter_shaft_bore_mm: float
    flap_height_mm: float
    flap_length_mm: float
    flap_thickness_mm: float
    flap_hub_outer_mm: float

    exhaust_transition_length_mm: float
    exhaust_transition_wall_mm: float
    exhaust_transition_outlet_mm: float

    material: str
    nozzle_mm: float
    layer_height_mm: float

    @property
    def diverter_inner_mm(self) -> float:
        return self.diverter_outer_mm - 2.0 * self.diverter_wall_mm

    def validate(self) -> None:
        positive = (
            self.printer_x_mm,
            self.printer_y_mm,
            self.printer_z_mm,
            self.diverter_outer_mm,
            self.diverter_wall_mm,
            self.diverter_port_mm,
            self.diverter_shaft_bore_mm,
            self.flap_height_mm,
            self.flap_length_mm,
            self.flap_thickness_mm,
            self.flap_hub_outer_mm,
            self.exhaust_transition_length_mm,
            self.exhaust_transition_wall_mm,
            self.exhaust_transition_outlet_mm,
            self.nozzle_mm,
            self.layer_height_mm,
        )
        if any(v <= 0 for v in positive):
            raise ValueError("ROUTING-V0.3 dimensions must be positive")

        if self.diverter_inner_mm <= 0:
            raise ValueError("diverter walls leave no internal chamber")
        if self.diverter_port_mm > self.diverter_inner_mm:
            raise ValueError("diverter port must fit inside the chamber opening")
        if self.flap_height_mm >= self.diverter_inner_mm:
            raise ValueError("flap height must fit inside diverter")
        if self.flap_length_mm >= self.diverter_inner_mm:
            raise ValueError("flap radial length must fit inside diverter")
        if self.flap_hub_outer_mm <= self.diverter_shaft_bore_mm:
            raise ValueError("flap hub must be larger than shaft bore")
        if self.exhaust_transition_outlet_mm > 120.0 - 2.0 * self.exhaust_transition_wall_mm:
            raise ValueError("exhaust transition outlet exceeds P12 body envelope")

        for x, y, z, label in (
            (
                self.diverter_outer_mm,
                self.diverter_outer_mm,
                self.diverter_outer_mm,
                "T-diverter",
            ),
            (
                120.0,
                120.0,
                self.exhaust_transition_length_mm,
                "exhaust fan transition",
            ),
        ):
            if x > self.printer_x_mm or y > self.printer_y_mm or z > self.printer_z_mm:
                raise ValueError(f"{label} exceeds printer envelope")


def _required(mapping: dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise ValueError(f"missing ROUTING-V0.3 key: {key}")
    return mapping[key]


def load_routing_v03_parameters(path: str | Path) -> RoutingV03Parameters:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    printer = _required(data, "printer")
    diverter = _required(data, "t_diverter")
    exhaust = _required(data, "exhaust_transition")
    printing = _required(data, "printing")

    p = RoutingV03Parameters(
        revision=str(_required(data, "revision")),
        printer_x_mm=float(_required(printer, "x_mm")),
        printer_y_mm=float(_required(printer, "y_mm")),
        printer_z_mm=float(_required(printer, "z_mm")),
        diverter_outer_mm=float(_required(diverter, "outer_mm")),
        diverter_wall_mm=float(_required(diverter, "wall_mm")),
        diverter_port_mm=float(_required(diverter, "port_mm")),
        diverter_shaft_bore_mm=float(_required(diverter, "shaft_bore_mm")),
        flap_height_mm=float(_required(diverter, "flap_height_mm")),
        flap_length_mm=float(_required(diverter, "flap_length_mm")),
        flap_thickness_mm=float(_required(diverter, "flap_thickness_mm")),
        flap_hub_outer_mm=float(_required(diverter, "flap_hub_outer_mm")),
        exhaust_transition_length_mm=float(_required(exhaust, "length_mm")),
        exhaust_transition_wall_mm=float(_required(exhaust, "wall_mm")),
        exhaust_transition_outlet_mm=float(_required(exhaust, "outlet_mm")),
        material=str(_required(printing, "material")),
        nozzle_mm=float(_required(printing, "nozzle_mm")),
        layer_height_mm=float(_required(printing, "layer_height_mm")),
    )
    p.validate()
    return p
