from pathlib import Path

import pytest

from hx import load_parameters
from routing import build_core_routing_adapter, build_p12_fan_pod


ROOT = Path(__file__).resolve().parents[1]


def test_p12_fan_pod_is_valid_and_fits_mega_s() -> None:
    params = load_parameters(ROOT / "parameters.yaml")
    pod = build_p12_fan_pod(params)
    bb = pod.val().BoundingBox()

    assert pod.val().isValid()
    assert bb.xlen == pytest.approx(params.fan_nominal_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(params.fan_nominal_mm, abs=1e-3)
    assert bb.zlen == pytest.approx(25.0, abs=1e-3)
    assert bb.xlen <= 200 and bb.ylen <= 200 and bb.zlen <= 200


def test_core_routing_adapter_matches_hx_v11_interface() -> None:
    params = load_parameters(ROOT / "parameters.yaml")
    adapter = build_core_routing_adapter(params)
    bb = adapter.val().BoundingBox()

    assert adapter.val().isValid()
    assert bb.xlen == pytest.approx(params.interface_flange_outer_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(params.interface_flange_outer_mm, abs=1e-3)
    assert bb.zlen == pytest.approx(params.interface_flange_thickness_mm, abs=1e-3)
    assert bb.xlen <= 200 and bb.ylen <= 200 and bb.zlen <= 200


def test_fan_pod_and_core_adapter_remove_air_passages() -> None:
    params = load_parameters(ROOT / "parameters.yaml")
    pod = build_p12_fan_pod(params)
    adapter = build_core_routing_adapter(params)

    full_pod_volume = params.fan_nominal_mm * params.fan_nominal_mm * 25.0
    full_adapter_volume = (
        params.interface_flange_outer_mm
        * params.interface_flange_outer_mm
        * params.interface_flange_thickness_mm
    )

    assert 0 < pod.val().Volume() < full_pod_volume
    assert 0 < adapter.val().Volume() < full_adapter_volume
