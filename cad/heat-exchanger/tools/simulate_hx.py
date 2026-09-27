from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt

from hx import load_parameters


AIR_RHO = 1.20          # kg/m3, representative indoor condition
AIR_MU = 1.81e-5        # Pa s
AIR_CP = 1005.0         # J/(kg K)
AIR_K = 0.0262          # W/(m K)
ENTRY_EXIT_K = 1.5      # estimated combined local-loss coefficient


@dataclass(frozen=True)
class Material:
    name: str
    density_kg_m3: float
    cp_j_kgk: float
    conductivity_w_mk: float
    note: str


MATERIALS = {
    "PETG": Material(
        "PETG",
        density_kg_m3=1270.0,
        cp_j_kgk=1200.0,
        conductivity_w_mk=0.20,
        note="illustrative printed PETG-like properties",
    ),
    "CERAMIC_GENERIC": Material(
        "CERAMIC_GENERIC",
        density_kg_m3=2200.0,
        cp_j_kgk=800.0,
        conductivity_w_mk=1.50,
        note="illustrative dense ceramic storage medium, not a selected product",
    ),
}


def core_pressure_point(p, flow_m3h: float) -> dict[str, float]:
    q = flow_m3h / 3600.0
    area = p.open_area_mm2 * 1e-6
    velocity = q / area
    dh = p.hydraulic_diameter_mm / 1000.0
    re = AIR_RHO * velocity * dh / AIR_MU

    if re < 1e-9:
        f = 0.0
    elif re < 2300.0:
        # Darcy friction factor for fully-developed square duct.
        f = 56.91 / re
    else:
        # Smooth-duct Blasius approximation.
        f = 0.3164 / (re ** 0.25)

    dynamic = 0.5 * AIR_RHO * velocity ** 2
    friction = f * (p.length_mm / 1000.0 / dh) * dynamic
    local = ENTRY_EXIT_K * dynamic
    total = friction + local

    fan_area = p.fan_aperture_area_mm2 * 1e-6
    fan_velocity = q / fan_area

    return {
        "flow_m3h": flow_m3h,
        "core_velocity_m_s": velocity,
        "fan_aperture_velocity_m_s": fan_velocity,
        "reynolds": re,
        "darcy_friction_factor": f,
        "friction_dp_pa": friction,
        "entry_exit_dp_pa": local,
        "estimated_core_dp_pa": total,
    }


def _heat_transfer_coefficient(p, material: Material) -> tuple[float, float]:
    dh = p.hydraulic_diameter_mm / 1000.0
    # Conservative fully-developed laminar square-duct Nusselt number.
    nu = 3.61
    h_air = nu * AIR_K / dh

    # Approximate conduction through half an internal wall plus air-side film.
    wall_half_m = (p.wall_thickness_mm / 1000.0) / 2.0
    u = 1.0 / (
        1.0 / h_air
        + wall_half_m / material.conductivity_w_mk
    )
    return h_air, u


def simulate_regenerator(
    p,
    *,
    flow_m3h: float,
    phase_time_s: float,
    material: Material,
    room_temp_c: float = 20.0,
    outside_temp_c: float = 0.0,
    segments: int = 24,
    cycles: int = 20,
    active_solid_fraction: float = 1.0,
) -> dict[str, float]:
    q = flow_m3h / 3600.0
    mdot = AIR_RHO * q
    if mdot <= 0:
        raise ValueError("flow must be positive")

    h_air, u = _heat_transfer_coefficient(p, material)

    surface_total = p.gross_internal_surface_area_m2
    ua_seg = u * surface_total / segments

    solid_volume_m3 = p.approximate_solid_volume_cm3 * 1e-6
    if not 0.0 < active_solid_fraction <= 1.0:
        raise ValueError("active_solid_fraction must be within (0, 1]")

    full_solid_capacity = (
        solid_volume_m3
        * material.density_kg_m3
        * material.cp_j_kgk
    )
    solid_capacity = full_solid_capacity * active_solid_fraction
    c_seg = solid_capacity / segments

    solids = [(room_temp_c + outside_temp_c) / 2.0] * segments
    dt = min(0.5, max(0.05, phase_time_s / 200.0))
    steps = max(1, int(round(phase_time_s / dt)))
    dt = phase_time_s / steps

    ntu_seg = ua_seg / (mdot * AIR_CP)
    exp_term = math.exp(-ntu_seg)

    last_supply_samples: list[float] = []
    last_exhaust_samples: list[float] = []

    def flow_once(t_in: float, indexes, collect: list[float]) -> None:
        nonlocal solids
        t_air = t_in
        new_solids = solids[:]
        for i in indexes:
            t_s = solids[i]
            t_out = t_s + (t_air - t_s) * exp_term
            qdot = mdot * AIR_CP * (t_air - t_out)
            new_solids[i] = t_s + qdot * dt / c_seg
            t_air = t_out
        solids = new_solids
        collect.append(t_air)

    for cycle in range(cycles):
        ex_samples: list[float] = []
        sup_samples: list[float] = []

        for _ in range(steps):
            flow_once(room_temp_c, range(segments), ex_samples)

        for _ in range(steps):
            flow_once(outside_temp_c, range(segments - 1, -1, -1), sup_samples)

        if cycle == cycles - 1:
            last_exhaust_samples = ex_samples
            last_supply_samples = sup_samples

    avg_supply = sum(last_supply_samples) / len(last_supply_samples)
    avg_exhaust = sum(last_exhaust_samples) / len(last_exhaust_samples)
    delta_t = room_temp_c - outside_temp_c
    eff_supply = (avg_supply - outside_temp_c) / delta_t
    eff_exhaust = (room_temp_c - avg_exhaust) / delta_t

    deadtime_duty = phase_time_s / (phase_time_s + p.switch_deadtime_s)

    core_void_l = (
        p.open_area_mm2 * p.length_mm / 1_000_000.0
    )
    exchange_l_per_phase = flow_m3h * 1000.0 / 3600.0 * phase_time_s
    void_fraction = core_void_l / exchange_l_per_phase

    thermal_diffusivity = (
        material.conductivity_w_mk
        / (material.density_kg_m3 * material.cp_j_kgk)
    )
    thermal_penetration_depth_mm = 1000.0 * math.sqrt(
        thermal_diffusivity * phase_time_s / math.pi
    )
    biot_half_wall = (
        h_air
        * (p.wall_thickness_mm / 2000.0)
        / material.conductivity_w_mk
    )

    return {
        "material": material.name,
        "active_solid_fraction": active_solid_fraction,
        "flow_m3h": flow_m3h,
        "phase_time_s": phase_time_s,
        "average_supply_out_c": avg_supply,
        "average_exhaust_out_c": avg_exhaust,
        "supply_effectiveness": eff_supply,
        "exhaust_effectiveness": eff_exhaust,
        "air_side_h_w_m2k": h_air,
        "effective_u_w_m2k": u,
        "solid_heat_capacity_j_k": solid_capacity,
        "full_solid_heat_capacity_j_k": full_solid_capacity,
        "thermal_penetration_depth_mm": thermal_penetration_depth_mm,
        "biot_half_wall": biot_half_wall,
        "deadtime_duty_fraction": deadtime_duty,
        "core_void_l": core_void_l,
        "air_exchange_per_phase_l": exchange_l_per_phase,
        "core_void_fraction_of_phase_exchange": void_fraction,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="parameters.yaml")
    ap.add_argument("--out", default="simulation/HX-V1.1")
    args = ap.parse_args()

    p = load_parameters(args.config)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    pressure_rows = [
        core_pressure_point(p, flow)
        for flow in range(10, 101, 10)
    ]
    write_csv(out / "pressure-drop-sweep.csv", pressure_rows)

    thermal_rows = []
    for material in MATERIALS.values():
        for flow in (20.0, 40.0, 60.0, 80.0):
            for phase in (30.0, 45.0, 60.0, 90.0):
                thermal_rows.append(
                    simulate_regenerator(
                        p,
                        flow_m3h=flow,
                        phase_time_s=phase,
                        material=material,
                    )
                )
    write_csv(out / "transient-thermal-sweep.csv", thermal_rows)

    # Sensitivity to how much of the thick frame participates thermally.
    participation_rows = []
    for fraction in (0.50, 0.75, 1.00):
        participation_rows.append(
            simulate_regenerator(
                p,
                flow_m3h=40.0,
                phase_time_s=60.0,
                material=MATERIALS["PETG"],
                active_solid_fraction=fraction,
            )
        )
    write_csv(
        out / "solid-participation-sensitivity.csv",
        participation_rows,
    )

    # Pressure chart.
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    ax.plot(
        [r["flow_m3h"] for r in pressure_rows],
        [r["estimated_core_dp_pa"] for r in pressure_rows],
        marker="o",
    )
    ax.set_xlabel("Flow per active module [m³/h]")
    ax.set_ylabel("Estimated core Δp [Pa]")
    ax.set_title(f"{p.revision}: core-only pressure estimate")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(out / "pressure-drop-sweep.png", dpi=160)
    plt.close(fig)

    # Thermal chart at 40 m3/h.
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    for material in MATERIALS:
        rows = [
            r for r in thermal_rows
            if r["material"] == material and r["flow_m3h"] == 40.0
        ]
        rows.sort(key=lambda r: r["phase_time_s"])
        ax.plot(
            [r["phase_time_s"] for r in rows],
            [100.0 * r["supply_effectiveness"] for r in rows],
            marker="o",
            label=material,
        )
    ax.set_xlabel("Pendulum phase time [s]")
    ax.set_ylabel("Simulated supply effectiveness [%]")
    ax.set_title(f"{p.revision}: simplified regenerative model at 40 m³/h")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "thermal-effectiveness-40m3h.png", dpi=160)
    plt.close(fig)

    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    ax.plot(
        [100.0 * r["active_solid_fraction"] for r in participation_rows],
        [100.0 * r["supply_effectiveness"] for r in participation_rows],
        marker="o",
    )
    ax.set_xlabel("Thermally participating solid mass [%]")
    ax.set_ylabel("Simulated supply effectiveness [%]")
    ax.set_title(
        f"{p.revision}: PETG storage participation sensitivity, 40 m³/h, 60 s"
    )
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(out / "solid-participation-sensitivity.png", dpi=160)
    plt.close(fig)

    summary = {
        "revision": p.revision,
        "assumptions": {
            "air_density_kg_m3": AIR_RHO,
            "air_dynamic_viscosity_pa_s": AIR_MU,
            "air_cp_j_kgk": AIR_CP,
            "air_conductivity_w_mk": AIR_K,
            "entry_exit_loss_k": ENTRY_EXIT_K,
            "thermal_model":
                "1D segmented solid matrix, quasi-steady air per segment, no axial solid conduction, no moisture phase change",
        },
        "materials": {
            k: material.__dict__ for k, material in MATERIALS.items()
        },
        "geometry": {
            "channel_width_mm": p.channel_width_mm,
            "hydraulic_diameter_mm": p.hydraulic_diameter_mm,
            "open_area_mm2": p.open_area_mm2,
            "surface_area_m2": p.gross_internal_surface_area_m2,
            "solid_volume_cm3": p.approximate_solid_volume_cm3,
        },
        "warnings": [
            "Core-only pressure model excludes filters, fans, plenums, bends, screens and inactive-fan drag.",
            "Thermal model is a screening model, not CFD or a validated heat-exchanger rating.",
            "Condensation, re-evaporation, frost and latent heat are not modeled.",
            "Material properties are illustrative assumptions and must be replaced by the actual printed/insert material.",
        ],
    }
    (out / "simulation-assumptions.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
