from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from simulate_hx import MATERIALS, core_pressure_point, simulate_regenerator
from hx import load_parameters


def test_pressure_drop_increases_with_flow() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    low = core_pressure_point(p, 20.0)
    high = core_pressure_point(p, 80.0)
    assert high["estimated_core_dp_pa"] > low["estimated_core_dp_pa"]
    assert low["reynolds"] > 0


def test_regenerator_effectiveness_is_physical() -> None:
    p = load_parameters(ROOT / "parameters.yaml")
    result = simulate_regenerator(
        p,
        flow_m3h=40.0,
        phase_time_s=60.0,
        material=MATERIALS["PETG"],
        cycles=12,
    )
    assert 0.0 < result["supply_effectiveness"] < 1.0
    assert 0.0 < result["deadtime_duty_fraction"] <= 1.0
    assert result["core_void_fraction_of_phase_exchange"] < 0.2
