from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_all_printed_components_fit_mega_s(tmp_path) -> None:
    out = tmp_path / "fit.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "check_printer_fit.py"),
            "--config",
            str(ROOT / "parameters.yaml"),
            "--printer",
            str(ROOT / "config" / "printers" / "anycubic-i3-mega-s.yaml"),
            "--out",
            str(out),
        ],
        check=True,
        cwd=ROOT,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert all(
        part["fits_with_margin"]
        for part in data["parts"].values()
    )
