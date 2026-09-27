# GL-C-211WL three-fan topology

## Decision

The project will use **one GLEDOPTO GL-C-211WL** as the central controller for **three ARCTIC P12 Pro PST fans**.

The three fans should be treated as **three independent logical PWM channels** even if two channels later receive the same target value.

## Electrical principle

The GL-C-211WL must not be treated as the 12 V speed-control power stage for a 4-pin PC fan.

Recommended topology:

```text
Mean Well LPV-35-12
12 V / 3 A
   |
   +--> P12 fan #1 +12 V
   +--> P12 fan #2 +12 V
   +--> P12 fan #3 +12 V
   |
   +--> GL-C-211WL
           |
           +--> GPIO / logic PWM #1 -> open-drain interface -> P12 #1 PWM
           +--> GPIO / logic PWM #2 -> open-drain interface -> P12 #2 PWM
           +--> GPIO / logic PWM #3 -> open-drain interface -> P12 #3 PWM
           |
           +--> optional servo-control GPIO -> MZ966 signal
```

The 12 V fan power remains continuous. Fan speed is controlled only through the 4-pin PWM input.

## Current-capacity check

Three P12 Pro PST fans at the manufacturer nominal current of 0.33 A each require about:

- 0.99 A total fan current
- 11.9 W at 12 V

This leaves substantial nominal capacity on the LPV-35-12 12 V / 3 A rail for the GL-C-211WL and the 12 V input side of the LK1263 servo converter.

However, the complete power budget must include:

- GL-C-211WL own consumption,
- LK1263 conversion losses,
- MZ966 servo peak current reflected to the 12 V input,
- cable voltage drop,
- startup/transient margin.

## Critical architecture mismatch to resolve

The current pendulum-control architecture still models **four logical directional fan roles**:

- room A supply fan
- room A exhaust fan
- room B supply fan
- room B exhaust fan

The newly confirmed hardware inventory contains **three physical fans**.

Therefore one of the following must be true before final hardware mapping:

1. one physical fan is shared between two logical roles,
2. one of the four logical roles is mechanically eliminated,
3. one module uses a different routing/damper arrangement,
4. the control architecture must be revised to a three-fan mechanical topology.

This mapping must be explicitly designed. It must not be hidden inside the WLED adapter.

## Software abstraction

The control core should continue to emit logical room/direction targets.

A separate hardware-mapping layer should convert those logical roles into the three physical fan channels.

Example unresolved hardware configuration:

```yaml
controller:
  id: gledopto-main
  model: GL-C-211WL

physical_fans:
  - id: fan-1
    pwm_channel: 1
  - id: fan-2
    pwm_channel: 2
  - id: fan-3
    pwm_channel: 3

logical_role_mapping:
  room_a_supply: TBD
  room_a_exhaust: TBD
  room_b_supply: TBD
  room_b_exhaust: TBD
```

The adapter must reject startup if this mapping is ambiguous or internally conflicting.

## Fan PWM channel requirements

Each fan channel needs:

- independent target 0–100%
- safe OFF on boot
- independent calibration factor
- command TTL/freshness check
- no retained non-zero transient command
- optional tach feedback if implemented
- deterministic all-off state during pendulum dead-time

## Servo coexistence

If the same GL-C-211WL also generates the MZ966 control signal, the selected GPIOs must satisfy all of the following:

- three stable fan-PWM outputs
- one stable RC-servo output
- no boot/reset glitch that can cause unsafe movement
- no conflict with WLED-internal pin assignments
- verified signal level and frequency behavior

The MZ966 servo remains powered from the separate LK1263 6 V / 3 A rail.

## Required bench work

- [ ] identify four usable logic-capable GPIOs or decide on an external fan/servo interface board
- [ ] scope three fan PWM outputs at boot and during runtime
- [ ] scope servo output at boot and during runtime
- [ ] verify three simultaneous fan PWM channels
- [ ] verify one fan OFF while others run
- [ ] verify all fans OFF during dead-time
- [ ] verify servo movement does not disturb fan PWM timing
- [ ] resolve three-physical-fan to four-logical-role mapping

## Gate

Do not freeze the Node-RED/WLED channel mapping until the three-fan mechanical topology is explicitly defined.
