from pathlib import Path

import pytest

from hx.parameters import HeatExchangerParameters, load_parameters


ROOT = Path(__file__).resolve().parents[1]


def test_default_parameters_load_and_validate() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    assert p.revision == "HX-V1.1"
    assert p.topology == "regenerative_matrix"
    assert p.paired_modules == 2
    assert p.channel_count == 18 * 18
    assert p.wall_thickness_mm == pytest.approx(0.8)
    assert p.perimeter_frame_mm == pytest.approx(3.2)
    assert p.channel_width_mm == pytest.approx(5.5555555556)
    assert p.channel_depth_mm == pytest.approx(5.5555555556)
    assert p.open_area_mm2 == pytest.approx(10000.0, abs=1e-5)
    assert p.sleeve_length_mm == pytest.approx(161.6)
    assert p.core_start_z_mm == pytest.approx(0.8)
    assert p.core_end_z_mm == pytest.approx(160.8)


def test_fan_and_matrix_open_areas_are_closely_matched() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    ratio = p.open_area_mm2 / p.fan_aperture_area_mm2
    assert 0.95 < ratio < 1.10


def test_print_wall_is_aligned_to_nozzle_strategy() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    unit = p.nozzle_mm / 2.0
    assert p.wall_thickness_mm / unit == pytest.approx(
        round(p.wall_thickness_mm / unit)
    )


def test_invalid_dense_geometry_is_rejected() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    invalid = HeatExchangerParameters(
        **{
            **p.__dict__,
            "width_mm": 10.0,
            "depth_mm": 10.0,
            "cells_x": 10,
            "cells_y": 10,
            "perimeter_frame_mm": 3.2,
            "wall_thickness_mm": 1.0,
        }
    )
    with pytest.raises(ValueError):
        invalid.validate()


def test_sleeve_stack_must_match_core_and_seals() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    invalid = HeatExchangerParameters(
        **{**p.__dict__, "sleeve_length_mm": p.sleeve_length_mm + 1.0}
    )
    with pytest.raises(ValueError):
        invalid.validate()
