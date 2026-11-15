from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from analyze_bench_csv import load_rows, summarize


def test_bench_analyzer_calculates_supply_effectiveness(tmp_path: Path) -> None:
    p = tmp_path / "bench.csv"
    fields = [
        "timestamp_iso","test_id","module","phase","fan_pwm_pct",
        "configuration","t_room_c","t_outside_c","t_module_out_c",
        "rh_room_pct","rh_outside_pct","rh_module_out_pct",
        "airflow_m3h","pressure_drop_pa","noise_dba","notes",
    ]
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerow({
            "timestamp_iso":"x","test_id":"supply-1","module":"A",
            "phase":"SUPPLY","fan_pwm_pct":"50",
            "configuration":"core-plus-stopped-fan",
            "t_room_c":"20","t_outside_c":"0","t_module_out_c":"10",
            "rh_room_pct":"70","rh_outside_pct":"60",
            "rh_module_out_pct":"65","airflow_m3h":"40",
            "pressure_drop_pa":"8","noise_dba":"35","notes":"",
        })

    report = summarize(load_rows(p))
    assert report["tests"]["supply-1"]["temperature_effectiveness_avg"] == 0.5
    assert report["configurations"]["core-plus-stopped-fan"]["airflow_m3h_avg"] == 40.0
