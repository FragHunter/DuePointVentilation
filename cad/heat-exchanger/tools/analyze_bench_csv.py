from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


NUMERIC_FIELDS = {
    "fan_pwm_pct",
    "t_room_c",
    "t_outside_c",
    "t_module_out_c",
    "rh_room_pct",
    "rh_outside_pct",
    "rh_module_out_pct",
    "airflow_m3h",
    "pressure_drop_pa",
    "noise_dba",
}


def _f(row: dict[str, str], key: str):
    value = row.get(key, "").strip()
    if not value:
        return None
    return float(value)


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in NUMERIC_FIELDS:
            row[key] = _f(row, key)
    return rows


def summarize(rows: list[dict]) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["test_id"]].append(row)

    tests = {}
    for test_id, group in groups.items():
        numeric_summary = {}
        for key in NUMERIC_FIELDS:
            values = [r[key] for r in group if r[key] is not None]
            if values:
                numeric_summary[key] = sum(values) / len(values)

        effectiveness = []
        for r in group:
            tr = r["t_room_c"]
            to = r["t_outside_c"]
            tm = r["t_module_out_c"]
            if tr is None or to is None or tm is None:
                continue
            denom = tr - to
            if abs(denom) < 0.5:
                continue

            phase = (r.get("phase") or "").upper()
            if phase == "SUPPLY":
                effectiveness.append((tm - to) / denom)
            elif phase == "EXHAUST":
                effectiveness.append((tr - tm) / denom)

        tests[test_id] = {
            "samples": len(group),
            "module": group[0].get("module"),
            "phase": group[0].get("phase"),
            "configuration": group[0].get("configuration"),
            "averages": numeric_summary,
            "temperature_effectiveness_avg": (
                sum(effectiveness) / len(effectiveness)
                if effectiveness else None
            ),
        }

    by_configuration: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_configuration[row.get("configuration") or "unknown"].append(row)

    configuration_summary = {}
    for config, group in by_configuration.items():
        flows = [r["airflow_m3h"] for r in group if r["airflow_m3h"] is not None]
        dps = [r["pressure_drop_pa"] for r in group if r["pressure_drop_pa"] is not None]
        configuration_summary[config] = {
            "samples": len(group),
            "airflow_m3h_avg": sum(flows) / len(flows) if flows else None,
            "pressure_drop_pa_avg": sum(dps) / len(dps) if dps else None,
        }

    return {
        "tests": tests,
        "configurations": configuration_summary,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_file", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    report = summarize(load_rows(args.csv_file))
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
