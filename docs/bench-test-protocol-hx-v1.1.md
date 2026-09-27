# HX-V1.1 bench test protocol

The first prototype is a measurement platform. The goal is to replace assumptions with measured airflow, pressure, temperature and moisture behavior.

## Measurement order

### Stage 1 — printer/process checks

1. print HX-V1.1 core coupon,
2. verify 0.8 mm wall production and channel openness,
3. print fit-core-plug and fit-sleeve-ring,
4. verify insertion clearance,
5. print fan-mount-gauge and confirm the actual ARCTIC P12 Pro PST hole pattern/aperture,
6. only then print full mechanical parts.

### Stage 2 — airflow baseline

At the same PWM values, record:

1. fan alone / open duct,
2. fan + plenum,
3. fan + plenums + empty sleeve,
4. fan + plenums + regenerative core,
5. fan + core + stopped opposite P12.

This isolates where pressure/flow is being lost.

Recommended PWM test points: 30, 50, 70 and 100 percent.

Record airflow and, where instrumentation is available, static pressure difference.

### Stage 3 — pendulum thermal response

Test at least 30 s, 45 s, 60 s and 90 s phase durations.

Record room temperature, outside/reference temperature and module outlet temperature throughout both EXHAUST and SUPPLY phases.

Do not infer effectiveness from one instantaneous sample. Use the phase-average temperature trajectory.

### Stage 4 — moisture behavior

With humid room-side air and colder outside-side air, observe:

- whether condensation forms,
- where it forms,
- whether it reaches the drain,
- whether liquid remains in core channels,
- whether outlet humidity rises after reversal,
- whether the next SUPPLY phase re-evaporates stored moisture.

For the DuePointVentilation project, net water removal matters more than maximum heat recovery.

### Stage 5 — room interaction

With both modules installed, test doors open, doors closed, and any known transfer opening.

Check whether the nominally balanced pair creates noticeable room pressure differences or routes air through unintended leaks.

## Data format

Use cad/heat-exchanger/test-data/templates/hx-v1.1-bench.csv.

Analyze a filled file with tools/analyze_bench_csv.py. The analyzer reports average airflow/pressure by configuration and phase temperature effectiveness where enough temperature difference exists.

## Decision gates

Do not freeze the axial opposed-fan architecture until stopped-fan flow restriction has been measured, condensate drainage has been demonstrated, outlet humidity after phase reversal has been observed, and actual heat recovery has been measured.

If stopped-fan drag or moisture re-evaporation is excessive, the next mechanical architecture is a branched fan path with dampers/bypass.
