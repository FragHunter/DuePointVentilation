# Miuzei MZ966 servo integration

## Research status

The exact public datasheet for a servo explicitly identified as **Miuzei MZ966** could not be located in current web research.

A verified Miuzei 6 V / 20 kg-class digital-servo datasheet for the DS3218 family lists:

- operating-voltage range: 4.8–6.8 V
- stall current: 1.8 A at 5 V
- stall current: 2.2 A at 6.8 V
- control signal: PWM pulse-width control
- pulse width: 500–2500 µs
- neutral: 1500 µs
- operating frequency: 50–330 Hz
- control-signal level shown as 3.3–5 V

Source:
https://engineering.purdue.edu/477grp10/Files/refs/servo.pdf

This is **reference-family data, not confirmed MZ966 data**. Market listings for similar Miuzei 20 kg servos are inconsistent, so the project must measure the actual MZ966 before freezing the power budget.

## Provisional current budget

Until the actual MZ966 is measured, use a **2.5 A per-servo stall-design allowance at 6 V**.

Reason:

- closest verified Miuzei 20 kg datasheet reaches 2.2 A at 6.8 V,
- other Miuzei 20 kg listings report still higher locked-current figures,
- 2.5 A provides a practical engineering allowance for the first bench test.

With the current LK1263 6 V / 3 A converter:

- one MZ966 may be operated/tested at a time,
- two servos must **not** be allowed to stall simultaneously,
- firmware should serialize servo movement until measured current proves otherwise,
- if two or more servos must move simultaneously under load, a larger 6 V rail or distributed converters may be required.

## Power wiring

Recommended power path:

```text
Mean Well LPV-35-12
12 V
  |
  +--> GL-C-211WL
  |
  +--> P12 fan power
  |
  +--> LK1263 DC/DC
          |
          +--> 6 V / 3 A servo rail
                  |
                  +--> MZ966 V+
                  +--> MZ966 GND
```

The servo power must not come from the ESP32/GPIO pin.

The servo signal ground and the GL-C-211WL/ESP32 signal ground must share the required common reference with the 6 V servo rail.

## Recommended control signal

The servo is controlled by **RC-servo pulse-width PWM**, not by the high-current LED PWM output.

Recommended first bench profile:

- frequency: **50 Hz**
- frame period: 20 ms
- initial neutral pulse: **1500 µs**
- initial conservative calibration window: **1000–2000 µs**
- extend toward 500–2500 µs only after confirming that the MZ966 does not hit a mechanical/electrical endpoint

Do not assume 0–180° corresponds exactly to any specific pulse range until the actual MZ966 has been calibrated.

## GL-C-211WL control approach

Preferred architecture for one servo per controller:

```text
Node-RED
   |
   | JSON/MQTT/HTTP command
   v
WLED on GL-C-211WL
   |
   | custom/usermod servo output
   v
free ESP32 GPIO / candidate IO33
   |
   | 3.3 V servo pulse signal
   v
MZ966 signal input

MZ966 power:
LK1263 6 V rail
```

Do **not** connect the servo signal wire to one of the GL-C-211WL high-current LED MOSFET outputs.

### Firmware options

1. **Preferred:** a small WLED usermod dedicated to the MZ966.
   - allocates one free GPIO
   - outputs 50 Hz RC-servo pulses
   - exposes target angle / pulse width through WLED JSON state
   - applies min/max calibrated endpoints
   - implements startup safe position / disable policy
   - reports last command and target

2. WLED community `pwm_outputs` usermod may be usable, but the exact frequency/pulse behavior must be verified on the installed WLED build before relying on it for the damper.

3. If the GL-C-211WL GPIO/firmware path proves awkward, use a separate small ESP32 servo controller and keep WLED only for fan/lighting-style outputs.

## Proposed Node-RED logical command

For the selected 2+1 fan topology, use **route names** instead of raw pulse widths:

```json
{
  "servo": "servo_route",
  "position": "ROOM_A_SUPPLY_ROOM_B_EXHAUST",
  "sequence": 42,
  "valid_until_ms": 1234567890
}
```

The actuator adapter maps:

- `ROOM_A_SUPPLY_ROOM_B_EXHAUST` -> calibrated route-A pulse
- `ROOM_B_SUPPLY_ROOM_A_EXHAUST` -> calibrated route-B pulse
- `SAFE` -> calibrated safe/service position

Raw pulse values remain device configuration, not control-flow logic.

The preferred ROUTING-V0.3 mechanism uses **two physically separate full-area T-diverters**. One logical servo command may mechanically couple their two shafts so the supply and exhaust routes switch together while the air bodies remain isolated. The earlier monolithic V0.2 double-diverter is superseded because its branch opening was only about 33% of the P12/core airflow area.

## Interlock policy

Servo/fan sequencing must be:

```text
fan OFF
  |
  v
servo move
  |
  v
wait until movement timeout / expected travel time
  |
  v
fan ON
```

For two servos on one 6 V / 3 A LK1263 rail, movement should initially be serialized:

```text
servo A move -> settle -> servo B move -> settle -> fans
```

This prevents two simultaneous startup/stall current peaks from exceeding the converter capability.

## MZ966 bench-current measurement

The exact MZ966 stall current should be measured before final power design.

Recommended test:

1. Use a 6.0 V supply capable of safely sourcing more than the expected current, with current limit.
2. Place an ammeter/current logger in series with servo V+.
3. Command neutral with no mechanical load and record idle/current-at-motion.
4. Sweep to each intended endpoint with no load.
5. Add representative damper load and record peak current.
6. Perform a **very brief** controlled stall/current-limit test only if needed; do not hold the servo stalled.
7. Repeat on each physical servo if multiple units are used.
8. Record maximum observed current plus margin.

Do not use the 3 A LK1263 itself as the only instrument for determining stall current, because converter current limiting/brownout can hide the servo's true peak demand.

## Measurements to record

- supply voltage at servo during movement
- idle current
- no-load movement peak
- representative damper movement peak
- endpoint current
- brief stall/current-limit peak if required
- movement time
- temperature rise
- pulse width for mechanical CLOSED
- pulse width for mechanical OPEN

## Current project decision

Until MZ966 measurements exist:

- primary project role: **routing actuator for the servo-routed 2+1 fan topology**
- preferred mechanics: one MZ966 linkage couples supply_t_diverter and exhaust_t_diverter shafts from ROUTING-V0.3
- position A = room A supply / room B exhaust
- position B = room B supply / room A exhaust
- design budget: **2.5 A per active servo at 6 V**
- only one servo moves at a time on the 3 A rail
- use 50 Hz / 1500 µs neutral as the starting signal
- start endpoint calibration at 1000–2000 µs
- use a GPIO/logic servo pulse, not a GL-C-211WL LED power output
- measured travel time plus settling margin defines the minimum safe fan dead-time
