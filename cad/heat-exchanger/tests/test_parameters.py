from pathlib import Path

import pytest

from hx.parameters import HeatExchangerParameters, load_parameters


ROOT = Path(__file__).resolve().parents[1]


def test_default_parameters_load_and_validate() -> None:
    params = load_parameters(ROOT / "parameters.yaml")

    assert params.revision == "HX-V1"
    assert params.topology == "regenerative_matrix"
    assert params.paired_modules == 2
    assert params.channel_count == 18 * 18
    assert params.channel_width_mm == pytest.approx(6.0333333333)
    assert params.channel_depth_mm == pytest.approx(6.0333333333)


def test_open_area_is_plausible() -> None:
    params = load_parameters(ROOT / "parameters.yaml")

    assert params.open_area_mm2 > 0
    assert 0.5 < params.open_area_ratio < 0.95
    assert params.gross_internal_surface_area_m2 > 0
    assert params.approximate_solid_volume_cm3 > 0


def test_invalid_dense_geometry_is_rejected() -> None:
    params = HeatExchangerParameters(
        revision="test",
        topology="regenerative_matrix",
        width_mm=10.0,
        depth_mm=10.0,
        length_mm=20.0,
        cells_x=10,
        cells_y=10,
        wall_thickness_mm=1.0,
        fan_nominal_mm=120.0,
        duct_nominal_mm=125.0,
        phase_time_s=60.0,
        switch_deadtime_s=3.0,
        material="test",
        nozzle_mm=0.4,
        layer_height_mm=0.2,
        removable_core=True,
        condensate_drain_required=True,
        reserve_bypass=True,
        paired_modules=2,
    )

    with pytest.raises(ValueError):
        params.validate()


def test_pair_count_is_currently_fixed_to_two() -> None:
    params = load_parameters(ROOT / "parameters.yaml")
    invalid = HeatExchangerParameters(
        **{**params.__dict__, "paired_modules": 3}
    )

    with pytest.raises(ValueError):
        invalid.validate()
