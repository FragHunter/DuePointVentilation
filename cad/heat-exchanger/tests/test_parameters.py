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
    assert params.routing_variant == "axial_opposed_fans"
    assert params.module_outer_mm == pytest.approx(128.8)
    assert params.module_total_length_mm == pytest.approx(258.0)


def test_open_area_is_plausible() -> None:
    params = load_parameters(ROOT / "parameters.yaml")

    assert params.open_area_mm2 > 0
    assert 0.5 < params.open_area_ratio < 0.95
    assert params.gross_internal_surface_area_m2 > 0
    assert params.approximate_solid_volume_cm3 > 0


def test_invalid_dense_geometry_is_rejected() -> None:
    params = load_parameters(ROOT / "parameters.yaml")
    invalid = HeatExchangerParameters(
        **{
            **params.__dict__,
            "width_mm": 10.0,
            "depth_mm": 10.0,
            "cells_x": 10,
            "cells_y": 10,
            "wall_thickness_mm": 1.0,
        }
    )

    with pytest.raises(ValueError):
        invalid.validate()


def test_pair_count_is_currently_fixed_to_two() -> None:
    params = load_parameters(ROOT / "parameters.yaml")
    invalid = HeatExchangerParameters(
        **{**params.__dict__, "paired_modules": 3}
    )

    with pytest.raises(ValueError):
        invalid.validate()
