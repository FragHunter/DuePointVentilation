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

Status: **exact model still missing**

Known:

- WLED/GLEDOPTO PWM controller is intended to drive the fan-control path.

Open checks:

- exact product/model/hardware revision
- output topology
- output PWM frequency
- whether output is a power PWM MOSFET output or a logic-level control output
- whether an interface circuit is required for the ARCTIC 4-pin PWM input
- WLED firmware/version

This remains the most important electrical compatibility gate.

## Servo system

### Miuzei 180-degree servos

Status: **planned later-stage actuator**

Role:

- future bypass/routing dampers
- possible branch isolation if the axial opposed-fan architecture has excessive stopped-fan drag

### DC/DC voltage converter LK1263

Status: **available / selected by user; electrical specifications still to verify**

Intended role:

- derive the servo supply from the 12 V system

Open checks before wiring:

- input-voltage range
- adjustable/fixed output voltage
- maximum continuous output current
- peak current capability
- efficiency
- thermal behavior
- whether one converter serves all servos or converters are distributed per module
- exact servo operating voltage and stall current

Do not freeze the servo power design until the LK1263 ratings and actual servo current are confirmed.

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
- LK1263 DC/DC converter -> servo supply -> Miuzei servos

The diagram is architectural only. The final fuse, wiring, distribution and interface design remains open until the GLEDOPTO and LK1263 electrical details are verified.
