# 3D-printed heat exchanger

## Status

Aqara Temperature and Humidity Sensor T1 devices remain the initial indoor/outdoor environmental sensors because they are already available for the project.

The next mechanical subsystem is a **3D-printed regenerative heat-storage core** for each of the two pendulum ventilation modules.

## Purpose

The heat exchanger shall recover sensible heat while the ventilation controller continues to decide **when ventilation is useful for drying** from indoor/outdoor moisture conditions.

In the paired pendulum architecture, each module alternates between exhaust and supply. The same core therefore sees warm room air in one phase and cold outside air in the next phase.

The core works as a **regenerator / thermal store**:

- EXHAUST phase: outgoing room air warms the core
- SUPPLY phase: incoming outside air recovers heat from the core
- the second room runs in the opposite direction so the pair remains approximately balanced
- ventilation eligibility is still based on indoor/outdoor absolute humidity / dew-point logic
- condensation and frost inside the core must be expected and managed

## Preferred first prototype

Start with a **single-path regenerative matrix core** that is traversed in both directions.

```text
MODULE A

PHASE 1 / EXHAUST:
room ─────► fan routing ─────► regenerative core ─────► outside
                                  stores heat

PHASE 2 / SUPPLY:
outside ──► fan routing ─────► regenerative core ─────► room
                                  releases heat
```

A second identical module in the other room operates 180 degrees out of phase.

Design goals:

- one common heat-storage flow path per module
- reversible system airflow by selecting intake vs exhaust function
- low pressure drop in both directions
- high internal surface area
- enough thermal mass to store useful heat over one pendulum phase
- condensate drainage in either flow direction
- removable/cleanable core or cartridge
- printable geometry with versioned parameters
- no large bypass around the core
- mechanical provision for future servo-controlled routing/bypass

The currently opened cross-flow CadQuery prototype is therefore an exploratory geometry only. The target CAD topology must pivot to a regenerative matrix suitable for alternating flow.

A fully printed polymer core is convenient to prototype, but its heat-storage behavior must be measured. If thermal performance is insufficient, the project can keep the printed housing/manifold while using a denser ceramic, metallic or other high-heat-capacity insert as the storage matrix.

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

For a regenerative core we should evaluate effectiveness over the phase, not only from one steady-state sample.

An initial instantaneous supply-side metric can still be logged:

```text
eta_t(t) = (T_supply_out(t) - T_outside)
           / (T_room - T_outside)
```

The project should additionally calculate a phase-average effectiveness. Only evaluate the metric when the room/outside temperature difference is sufficiently large.

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

Known now:

- two modules exist
- they are installed in two rooms
- they can operate as a synchronized pendulum pair
- one module supplies while the other exhausts, then the roles swap

Still to resolve before the final CAD geometry is frozen:

1. do the intake and exhaust fans of one module share one physical duct/core path, or are they on separate routed paths?
2. target airflow per active module in m³/h?
3. initial phase duration (for example 30–90 s, to be tuned experimentally)?
4. room volumes and desired air-change rate?
5. maximum available module/core dimensions?
6. 3D printer build volume?
7. intended filament/material?
8. preferred duct/fan interface dimensions?
9. required noise limit?
10. module mounting orientation?
11. direct condensate drain available?
12. should revision 1 already include a bypass/routing flap?
13. should the heat-storage core be a removable cartridge?
14. are the two rooms connected by a sufficient transfer-air path when doors are closed?
