from pathlib import Path

import pytest

from hx.parameters import HeatExchangerParameters, load_parameters


ROOT = Path(__file__).resolve().parents[1]


def test_default_parameters_load_and_validate() -> None:
    params = load_parameters(ROOT / "parameters.yaml")

    assert params.revision == "HX-V1"
    assert params.channel_count == 24
    assert params.plate_count == 25
    assert params.x_flow_channels == 12
    assert params.y_flow_channels == 12
    assert params.total_height_mm == pytest.approx(107.25)


def test_open_area_is_positive() -> None:
    params = load_parameters(ROOT / "parameters.yaml")

    assert params.x_flow_open_area_mm2 > 0
    assert params.y_flow_open_area_mm2 > 0


def test_invalid_rail_geometry_is_rejected() -> None:
    params = HeatExchangerParameters(
        revision="test",
        topology="cross_flow_plate_stack",
        width_mm=10.0,
        depth_mm=10.0,
        channel_count=4,
        channel_height_mm=2.0,
        plate_thickness_mm=0.4,
        rail_thickness_mm=5.0,
        fan_nominal_mm=120.0,
        duct_nominal_mm=125.0,
        material="test",
        nozzle_mm=0.4,
        layer_height_mm=0.2,
        removable_core=True,
        condensate_drain_required=True,
        reserve_bypass=True,
    )

    with pytest.raises(ValueError):
        params.validate()
