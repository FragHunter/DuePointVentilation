# 3D-printed heat exchanger

## Status

Aqara Temperature and Humidity Sensor T1 devices remain the initial indoor/outdoor environmental sensors because they are already available for the project.

The next mechanical subsystem is a **3D-printed air-to-air heat exchanger** placed between the active intake and exhaust air paths.

## Purpose

The heat exchanger shall recover sensible heat while the ventilation controller continues to decide **when ventilation is useful for drying** from indoor/outdoor moisture conditions.

A normal plate/counter-flow heat exchanger primarily transfers heat, not water vapor. Therefore:

- ventilation eligibility is still based on indoor/outdoor absolute humidity / dew-point logic
- heat recovery changes the supply-air temperature and therefore its relative humidity
- condensation inside the exchanger must be expected and managed
- a condensate drain is part of the design, not an optional afterthought

## Preferred first prototype

Start with a **separated-air-stream plate heat exchanger**, preferably counter-flow or cross-counter-flow.

Design goals:

- two fully separated air paths
- low pressure drop
- large transfer area
- thin transfer walls
- no short-circuit between intake and exhaust
- removable/cleanable core or housing
- controlled condensate path
- printable as modules so geometry can be iterated without reprinting the complete installation
- interfaces sized for the selected intake/exhaust fans and ducts

Concept:

```text
OUTSIDE AIR ──► intake fan ──►┌─────────────────────┐──► supply to room
                              │                     │
                              │  printed heat       │
                              │  exchanger core     │
                              │                     │
ROOM AIR ─────► exhaust fan ─►└─────────────────────┘──► exhaust outside
```

The final fan placement (push/pull relative to the core) is a test item because noise, leakage and pressure behavior can differ.

## Instrumentation during development

For the production control loop, the existing indoor and outdoor Aqara T1 sensors are sufficient to decide whether outside air is drier than room air.

For exchanger development, four temperature measurement points are desirable:

1. outside air before exchanger
2. supply air after exchanger
3. room/extract air before exchanger
4. exhaust air after exchanger

This enables measurement of temperature efficiency and detection of unexpected heat losses.

Humidity measurement before/after the exchanger is useful for condensation studies, but does not need to be part of the first control-loop implementation.

## Measured performance

The project should calculate and log at least:

- intake temperature before exchanger
- supply temperature after exchanger
- extract temperature before exchanger
- exhaust temperature after exchanger
- intake/exhaust fan targets
- airflow estimate or measured airflow
- pressure drop if measurement hardware is available
- condensate observations
- exchanger temperature efficiency

A simple supply-side temperature effectiveness metric:

```text
eta_t = (T_supply_after - T_outside_before)
        / (T_extract_before - T_outside_before)
```

Only use the metric when the denominator is sufficiently large; otherwise the value becomes numerically meaningless.

## Condensation management

The exhaust-air side can cross its dew point as it cools.

The mechanical design therefore needs:

- a defined low point
- condensate collection channel
- drain outlet
- no pockets where water can remain trapped
- geometry that prevents condensate from entering electronics or fans
- access for inspection and cleaning

Node-RED should eventually expose:

- CONDENSATION_EXPECTED
- FROST_RISK
- HEAT_EXCHANGER_BYPASS

as explicit control/status concepts.

## Frost behavior

At low outdoor temperature, condensate can freeze in the exchanger and progressively block airflow.

Potential later strategies:

- reduce airflow
- intermittent defrost cycle
- temporarily stop intake while extract continues
- exchanger bypass
- preheater (only if ever required)

The first prototype should **measure behavior before automating defrost**.

## Pressure drop is a primary design constraint

The heat exchanger adds flow resistance. A thermally excellent core that reduces airflow too far is not useful.

For every geometry revision record:

- channel dimensions
- core length
- number of channels/plates
- wall thickness
- fan PWM
- estimated/measured airflow
- pressure drop where possible
- acoustic behavior

The design should be optimized jointly for heat transfer and pressure loss.

## FDM-specific notes

A printed exchanger introduces engineering issues that do not exist with commercial metal/polymer plate cores:

- layer-line leakage between air streams
- variable wall thickness
- rough channel surfaces and increased pressure loss
- difficult cleaning of narrow channels
- trapped condensate
- material aging in continuously humid conditions

Therefore every prototype must receive an **air-leak test** before use.

The project should keep material and print parameters in version-controlled metadata:

```yaml
heat_exchanger:
  revision: hx-v1
  material: TBD
  nozzle_mm: TBD
  layer_height_mm: TBD
  wall_thickness_mm: TBD
  core_length_mm: TBD
  channel_width_mm: TBD
  channel_height_mm: TBD
```

## Bypass

A bypass is strongly recommended in the mechanical architecture even if it is not implemented in revision 1.

Reasons:

- summer operation where heat recovery is undesirable
- free cooling
- frost/defrost strategy
- fault operation
- comparison testing of exchanger vs direct ventilation

The future Miuzei 180° servo subsystem can operate the bypass/damper mechanism.

## Safety / hygiene

The exchanger should be:

- inspectable
- cleanable
- drainable
- resistant to the expected humidity and temperature range
- designed so outside/exhaust air cannot leak significantly into the supply stream

A filter interface on the outside-air path should be considered before final mechanical design.

## Open design decisions

Before CAD work starts, resolve:

1. one exchanger per ventilation installation or one central exchanger?
2. target airflow in m³/h?
3. room volume and desired air-change rate?
4. maximum available exchanger dimensions?
5. 3D printer build volume?
6. intended filament/material?
7. preferred duct/fan interface dimensions?
8. required noise limit?
9. exchanger mounting orientation?
10. direct condensate drain available?
11. should the first revision already include a bypass?
12. should the heat-exchanger core be replaceable as a cartridge?
