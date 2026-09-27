# ARCTIC P12 Pro PST fail-safe PWM interface

## Status

Engineering candidate for bench validation. The circuit is intentionally not a
final GPIO assignment or production PCB until the real GL-C-211WL signal nodes
are identified and scoped.

## Verified fan-side requirements

ARCTIC documents for the P12 Pro PST:

- fan power: 12 V DC
- fan current: 0.33 A nominal
- 4-pin connector
- PWM target frequency: 25 kHz
- accepted PWM frequency range: 21-28 kHz
- maximum logic-low voltage: 0.8 V
- maximum sourced/short-circuit current on the PWM interface: 5 mA
- maximum open-circuit PWM voltage: 5.25 V
- 0 rpm below 5 % PWM

Manufacturer sources:

- https://www.arctic.de/en/P12-Pro-PST/ACFAN00306A
- https://support.arctic.de/de/p12-pro-pst

The fan 12 V power remains continuous. Speed control is only on pin 4 PWM.

## Why not direct ESP32 GPIO

The PWM input can sit above the ESP32 3.3 V rail when released. Therefore the
project must not assume that direct push-pull connection from an ESP32 GPIO is
safe.

The GL-C-211WL LED power terminals are also not fan-PWM logic outputs and must
not be connected directly to pin 4 of the fan.

## Supply-bank parallel PWM calculation

fan_1 and fan_2 always receive the same supply-bank PWM target, so their PWM
inputs may share one sink node after bench validation.

ARCTIC specifies up to 5 mA sourced/short-circuit current per PWM input.
Therefore the conservative worst-case sink requirement is:

- one fan: <= 5 mA
- two parallel supply fans: <= 10 mA

The selected sink device must comfortably exceed 10 mA while keeping the fan
PWM node below 0.8 V in the LOW state.

Do not parallel the tachometer outputs. If RPM monitoring is added, keep tach
signals separate or intentionally monitor only one fan per bank.

## Fail-safe two-stage sink concept

A simple open-drain transistor with a gate/base pulldown would fail in the
wrong direction: controller reset/high-Z would release the fan PWM line and may
command full speed.

The preferred candidate therefore uses two stages so loss/reset of the ESP
logic defaults the fan PWM line LOW.

Concept per PWM group:

    +12 V fan rail
       |
      R1 10 kOhm candidate
       |
       +------ gate Q1 N-MOSFET
       |             drain ------ PWM to fan pin 4
       |             source ----- GND
       |
       C Q2 NPN
    GPIO--R2--B
       |     E
      R3     |
       |    GND
      GND

Candidate starting values:

- R1: 10 kOhm gate pull-up to the same 12 V fan rail
- R2: 10 kOhm ESP-to-Q2 base resistor
- R3: 100 kOhm Q2 base pulldown

These resistor values are bench starting values, not production-frozen values.

### Q1 requirements

Use a small low-gate-charge N-channel MOSFET with at least:

- VDS rating comfortably above 5.25 V
- VGS rating compatible with the 12 V pull-up, preferably +/-20 V or greater
- sink capability comfortably above 10 mA
- low enough gate charge for clean 25 kHz operation with R1

Q1 only sinks the fan PWM input; it never switches the 12 V motor current.

### Q2 requirements

Use a small NPN transistor with:

- collector voltage rating comfortably above 12 V
- enough gain to pull the Q1 gate close to ground while sinking the R1 current
- base drive compatible with 3.3 V ESP logic through R2

With R1 = 10 kOhm at 12 V, Q2 only needs to sink roughly 1.2 mA from R1 plus
transient gate current.

## Logic behavior

The two-stage topology intentionally gives intuitive control polarity:

- ESP GPIO LOW or high-Z -> Q2 OFF -> R1 turns Q1 ON -> fan PWM LOW -> fan OFF
- ESP GPIO HIGH -> Q2 ON -> Q1 OFF -> fan internal pull-up makes PWM HIGH -> fan ON
- 25 kHz ESP duty therefore corresponds directly to desired fan PWM duty

At ESP reset/high-Z, Q2 base pulldown keeps Q2 off and the +12 V pull-up drives
Q1 on. As long as the fan 12 V rail exists, the PWM node is actively pulled
LOW rather than floating to the fan's released state.

This hardware default complements, rather than replaces, the software actuator
interlock.

## Proposed group count

The selected 2+1 topology only needs two fan-PWM interface groups:

1. SUPPLY_PWM
   - fan_1 PWM
   - fan_2 PWM
   - conservative sink requirement <= 10 mA

2. EXHAUST_PWM
   - fan_3 PWM
   - conservative sink requirement <= 5 mA

The servo is a third, separate RC-servo pulse output and does not use this
25 kHz fan interface.

## GL-C-211WL implications

GLEDOPTO documents the GL-C-211WL as an ESP32 analog PWM LED controller with
LED GPIO assignments 19, 18, 17, 16 and 4, plus DIY interface IO33.

Manufacturer source:
https://gledopto.com/h-pd-100.html

The manual also warns that GPIO16/default output may flash after reset.

That documentation does not by itself prove that the external LED terminals
are raw 3.3 V GPIO signals. The project must identify the actual logic node or
use a separate controller/interface board.

Do not freeze GPIO assignment until the real board has been checked for:

- raw ESP signal versus power-MOSFET-switched terminal
- voltage levels
- boot/reset state
- WLED pin ownership
- ability to generate stable 21-28 kHz fan PWM
- ability to generate the separate RC-servo signal

## Bench test — one fan

1. Power the P12 continuously from 12 V.
2. Connect only GND and the candidate PWM interface.
3. Scope fan pin 4 at the fan connector.
4. Verify controller reset/high-Z keeps the PWM node LOW and the fan stopped.
5. Verify 0 % command keeps PWM LOW and fan stopped.
6. Verify 25/50/75/100 % commands at nominal 25 kHz.
7. Record LOW voltage; it must remain below the ARCTIC 0.8 V limit.
8. Record waveform rise/fall behavior and duty distortion.
9. Record RPM/start threshold if tach is available.
10. Power-cycle controller and fan rail independently where possible.

## Bench test — two parallel supply fans

After the one-fan test passes:

1. Join fan_1 and fan_2 PWM pin 4 to SUPPLY_PWM.
2. Keep tachometer outputs separate.
3. Repeat 0/25/50/75/100 %.
4. Measure LOW voltage with both internal fan sources active.
5. Verify both fans stop at 0 %.
6. Verify both start reliably and follow duty together.
7. Scope for slower edges, ringing or duty distortion.
8. Measure/confirm interface sink current if practical.
9. Power-cycle and reset the controller; both fans must default OFF.

## Acceptance gate

Do not freeze the fan interface until:

- one-fan waveform passes,
- two-fan shared supply PWM passes,
- LOW remains < 0.8 V,
- nominal frequency is within 21-28 kHz,
- reset/high-Z leaves fans OFF,
- 0 % leaves fans stopped,
- no unsafe boot pulse is observed,
- WLED/ESP pin ownership is stable,
- the servo output can coexist without disturbing fan PWM timing.
