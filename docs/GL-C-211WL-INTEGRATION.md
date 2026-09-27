# GLEDOPTO GL-C-211WL integration notes

Selected controller: **GLEDOPTO GL-C-211WL**

Manufacturer source:
https://gledopto.com/h-pd-100.html

Verified public specifications:

- ESP32 WLED PWM LED controller
- input voltage: 12–24 V DC
- total output current: 15 A max
- output current per channel: 10 A max
- Wi-Fi
- IP20
- size: 108 × 45 × 18 mm
- documented LED PWM GPIO channels: GPIO19, GPIO18, GPIO17, GPIO16, GPIO4
- DIY interface: IO33

## Important implication for ARCTIC P12 Pro PST

The GL-C-211WL is designed as an analog PWM LED-strip controller. Its normal high-current outputs must **not** be assumed to be directly compatible with the 4-pin PC-fan PWM logic input.

The P12 Pro PST should receive:

- continuous 12 V fan power,
- a dedicated fan PWM control signal,
- common reference/ground as required,
- optional tach feedback separately.

The GL-C-211WL can still serve as the WLED/ESP32 network/control endpoint, but the fan-control electrical interface must be measured and validated.

## Candidate integration paths

### Path A — exposed ESP32/DIY GPIO plus fan-PWM interface

Preferred if the installed firmware can produce the required fan PWM timing on a usable GPIO.

Typical concept:

ESP32 logic -> fail-safe two-stage sink interface -> P12 PWM input

The preferred candidate defaults the PWM node LOW when the ESP signal is LOW/high-Z, so controller reset does not simply release the fan input. See P12-PWM-FAILSAFE-INTERFACE.md.

LPV-35-12 12 V -> P12 power

### Path B — separate fan-PWM controller

Use if the GL-C-211WL cannot generate a stable suitable fan-control signal.

### Path C — dedicated ESP32 fan-control device/firmware

Use if repurposing the GL-C-211WL pins/firmware proves fragile.

## Verified P12 PWM electrical limits

ARCTIC documents 25 kHz target / 21-28 kHz accepted PWM, logic LOW <= 0.8 V,
maximum 5 mA sourced/short-circuit current and maximum 5.25 V open-circuit
voltage on the PWM input.

For fan_1 + fan_2 in parallel, design the shared SUPPLY_PWM sink for at least
the conservative 2 x 5 mA = 10 mA input-source bound. EXHAUST_PWM only drives
fan_3 and therefore has the single-fan 5 mA bound.

Do not parallel tachometer outputs.

Detailed circuit and bench procedure: P12-PWM-FAILSAFE-INTERFACE.md

## Bench verification required

- [ ] record actual GL-C-211WL hardware revision
- [ ] record WLED firmware version
- [ ] identify true switched LED outputs versus exposed logic/GPIO
- [ ] measure candidate signal voltage
- [ ] measure PWM frequency with oscilloscope/logic analyzer
- [ ] verify 0/25/50/75/100% duty behavior
- [ ] verify boot/reset/Wi-Fi reconnect behavior
- [ ] verify no unsafe startup pulse
- [x] define fail-safe two-stage fan-PWM interface candidate; physical validation still required
- [ ] only then connect the P12 PWM control input

## Boot/reset consideration

The controller manual notes that GPIO16 is a default output and may briefly flash after reset. Treat GPIO16 as unsuitable for safety-critical fan control unless startup behavior is explicitly tested and controlled.

## Current power concept

230 V AC -> Mean Well LPV-35-12 -> 12 V DC bus

12 V bus:
- GL-C-211WL power
- P12 fan power
- LK1263 DC/DC -> Miuzei servo rail

The P12 speed-control signal should remain electrically separate from its 12 V power feed.

## Decision gate

Do not connect the P12 PWM input directly to a GL-C-211WL high-current LED output until the signal level, topology and PWM behavior are measured.
