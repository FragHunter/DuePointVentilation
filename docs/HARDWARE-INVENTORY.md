# DuePointVentilation — Hardware inventory

This file records hardware that is actually available or explicitly selected for the project. Unknown electrical/mechanical details remain marked as verification items.

## Power supply

### Mean Well LPV-35-12

Status: **available / selected**

Verified manufacturer specifications:

- output: 12 V DC
- rated current: 3 A
- rated output power: 36 W
- constant-voltage supply
- IP67 encapsulated housing
- Class II / no protective-earth output reference
- AC input: 90–264 V AC according to the manufacturer datasheet

Project role:

- primary 12 V DC supply for the ventilation electronics/fans
- possible upstream source for the servo DC/DC converter

Open checks:

- complete current budget for all P12 fans, GLEDOPTO controller, DC/DC converter and servo peak loads
- fuse/protection concept
- connector/wire gauge
- whether one LPV-35-12 supplies both room modules or one supply is used per module
- cable voltage drop to both modules

## Fans

### ARCTIC P12 Pro PST

Status: **selected**

Manufacturer specifications relevant to this project:

- 12 V DC
- 0.33 A per fan
- 4-pin PWM
- 600–3000 rpm
- 0 rpm below 5 % PWM
- 120 × 120 × 25 mm
- target PWM frequency 25 kHz; documented acceptable range 21–28 kHz

Project architecture currently assumes:

- two fans per module
- two room modules
- only one directional fan per module active in normal pendulum operation

Open checks:

- real fan-mount fit using the generated gauge
- exact startup/minimum stable PWM with the actual controller path
- stopped-fan aerodynamic restriction
- whether tach feedback will be captured

## GLEDOPTO / WLED controller

### GLEDOPTO GL-C-211WL

Status: **available / selected; fan-interface validation still open**

Verified public manufacturer/manual data:

- ESP32 WLED PWM LED controller
- input: 12–24 V DC
- total output current: 15 A max
- output current/channel: 10 A max
- Wi-Fi
- IP20
- 108 × 45 × 18 mm
- documented PWM LED-strip GPIO channels: GPIO19, GPIO18, GPIO17, GPIO16, GPIO4
- DIY interface: IO33

Project implication:

The GL-C-211WL is an analog LED-strip PWM controller. The normal high-current outputs must not be assumed to be directly compatible with the 4-pin P12 PWM logic input.

Preferred project direction is to power the P12 continuously from the 12 V rail and use a verified logic/open-drain interface from a suitable ESP32/GPIO signal if the required PWM behavior can be generated reliably.

Open checks:

- actual hardware revision
- installed WLED firmware/version
- exact electrical output-stage topology
- candidate GPIO signal voltage/frequency/duty behavior
- boot/reset behavior
- fan PWM interface transistor/open-drain stage if required
- tach feedback strategy

See `GL-C-211WL-INTEGRATION.md`.

## Servo system

### Miuzei 180-degree servos

Status: **planned later-stage actuator**

Role:

- future bypass/routing dampers
- possible branch isolation if the axial opposed-fan architecture has excessive stopped-fan drag

### DC/DC voltage converter LK1263

Status: **available / selected**

Known project output:

- output voltage: **6 V DC**
- maximum output current: **3 A**
- maximum output power at the stated rating: **18 W**

Intended role:

- derive the 6 V servo rail from the 12 V LPV-35-12 system

Open checks before wiring:

- input-voltage range
- efficiency at expected load
- thermal behavior
- whether 3 A is a continuous rating or requires derating/cooling
- whether one converter serves all servos or converters are distributed per module
- actual Miuzei servo operating-voltage range
- actual Miuzei stall current and simultaneous-movement peak current

Do not freeze the servo power design until the actual servo current is confirmed against the 6 V / 3 A converter limit.

## Sensors

### Aqara Temperature and Humidity Sensor T1

Status: **available / selected**

Use:

- indoor room A
- indoor room B
- outdoor reference sensor in a suitable ventilated weather/radiation shield

Open checks:

- Zigbee coordinator
- Zigbee2MQTT deployment
- real reporting cadence
- side-by-side calibration
- outdoor shield

## 3D printer

### Anycubic i3 Mega S

Status: **available / target printer**

Project planning profile:

- nominal manufacturer build volume: 210 × 210 × 205 mm
- conservative project envelope: 200 × 200 × 200 mm
- current CAD assumes 0.4 mm nozzle
- current starting material: PETG
- current layer-height starting point: 0.20 mm

Open checks:

- actual installed nozzle size
- actual PETG brand/profile
- dimensional calibration using the generated HX-V1.1 coupons/gauges

## Current power-path concept

230 V AC -> Mean Well LPV-35-12 -> 12 V DC bus

From the 12 V bus:
- P12 fan supply / GLEDOPTO-WLED path
- LK1263 DC/DC converter -> **6 V / 3 A servo rail** -> Miuzei servos

The diagram is architectural only. The LK1263 output is now known as 6 V / 3 A; the final fuse, wiring, distribution and servo-current budget remain open until the Miuzei stall/peak current is verified.
