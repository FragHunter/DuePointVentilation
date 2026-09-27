from pathlib import Path

import pytest

from hx import build_module_shell, load_parameters


ROOT = Path(__file__).resolve().parents[1]


def test_module_shell_bounding_box_matches_parameters() -> None:
    params = load_parameters(ROOT / "parameters.yaml")
    shell = build_module_shell(params)
    bb = shell.val().BoundingBox()

    assert bb.xlen == pytest.approx(params.module_outer_mm, abs=1e-3)
    assert bb.ylen == pytest.approx(params.module_outer_mm, abs=1e-3)
    assert bb.zlen == pytest.approx(params.module_total_length_mm, abs=0.1)
    assert shell.val().Volume() > 0
