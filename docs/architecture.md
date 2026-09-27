# System architecture

## Functional layers

```text
┌──────────────────────────────────────────────┐
│                 Sensor layer                 │
│ Aqara T1 indoor / outdoor / optional extras │
└──────────────────────┬───────────────────────┘
                       │ Zigbee 3.0
                       ▼
┌──────────────────────────────────────────────┐
│            Zigbee transport layer            │
│ Coordinator + Zigbee2MQTT                   │
└──────────────────────┬───────────────────────┘
                       │ MQTT
                       ▼
┌──────────────────────────────────────────────┐
│              Orchestration layer             │
│ Node-RED                                     │
│                                              │
│ - normalize sensor data                      │
│ - validate freshness/plausibility            │
│ - calculate dew point                        │
│ - calculate absolute humidity                │
│ - evaluate condensation risk                 │
│ - run ventilation state machine              │
│ - determine fan targets                      │
│ - manage manual override                     │
│ - publish status / alarms                    │
└───────────────┬─────────────────┬────────────┘
                │                 │
                │ MQTT/HTTP       │ time series
                ▼                 ▼
┌─────────────────────────┐   ┌─────────────────┐
│     Actuator adapter    │   │ Monitoring      │
│ WLED / GLEDOPTO         │   │ InfluxDB/Grafana│
└─────────────┬───────────┘   └─────────────────┘
              │
       ┌──────┴──────┐
       ▼             ▼
  intake fan     exhaust fan
       \             /
        \           /
         ▼         ▼
       3D-printed air-to-air
          heat exchanger
         /             \
        ▼               ▼
  supply to room    exhaust outside

Future actuator path:
Node-RED → servo adapter → intake/exhaust dampers
```

## Installation model

One installation is one controlled ventilation zone.

```yaml
installation:
  id: cellar-east

  sensors:
    indoor: aqara-cellar-east
    outdoor: aqara-outside-north

  fans:
    intake:
      controller: wled-cellar-east
      channel: 0

    exhaust:
      controller: wled-cellar-east
      channel: 1

  dampers:
    enabled: false
```

Outdoor sensors may be shared between several zones.

## Control inputs

Required:

- indoor temperature
- indoor relative humidity
- outdoor temperature
- outdoor relative humidity
- measurement timestamps

Derived:

- indoor dew point
- outdoor dew point
- indoor absolute humidity
- outdoor absolute humidity
- absolute-humidity delta
- optional condensation margin against measured surface temperature

## Control output

The controller emits logical targets independent of hardware:

```json
{
  "installation_id": "cellar-east",
  "state": "VENTILATING",
  "reason": "OUTSIDE_AIR_DRIER",
  "intake_pct": 65,
  "exhaust_pct": 65
}
```

The WLED adapter maps these logical targets to the actual GLEDOPTO controller.

## Initial state machine

```text
                 conditions true
        ┌────────────────────────────┐
        │                            ▼
      OFF ──────► STARTING ─────► VENTILATING
       ▲                              │
       │                              │ stop condition
       │                              ▼
       └──────────── COOLDOWN ◄───────┘

Fault/override states:
- MANUAL
- SENSOR_FAULT
- CONTROLLER_FAULT
- FROST_LOCKOUT
- CONDENSATION_LOCKOUT
```

## Initial control policy

The exact thresholds remain configuration values and will be validated experimentally.

Initial concepts:

- start only when outside air has sufficiently lower absolute humidity than inside air
- use separate start/stop thresholds for hysteresis
- minimum runtime
- minimum off-time
- stale sensor timeout
- configurable minimum outdoor temperature
- optional condensation protection using surface temperature
- no automatic ventilation if a required sensor is stale or invalid
- manual override must expire automatically

## Cross ventilation and heat recovery

Each zone uses an active intake and an active exhaust fan. The mechanical air paths may pass through a printed air-to-air heat exchanger. The exchanger remains a mechanical subsystem: Node-RED still decides ventilation from the indoor/outdoor moisture state, while heat recovery reduces thermal losses.

Condensate handling, pressure drop, exchanger leakage and frost behavior are treated as explicit design/test items. The architecture reserves a future bypass path that can be actuated by the planned servo subsystem.

Each zone uses an active intake and an active exhaust fan.

Initial mode:

```text
intake target == exhaust target
```

Later modes may deliberately create a small pressure bias:

- exhaust-dominant
- intake-dominant
- adaptive balancing

Those modes must be explicit configuration, not accidental mismatched PWM values.

## Hardware abstraction

Control logic must not know:

- WLED IP addresses
- GLEDOPTO channel numbers
- Zigbee IEEE addresses
- raw Zigbee2MQTT field names

These belong to adapters/configuration.

This separation allows future replacement of:

- Zigbee2MQTT
- WLED
- GLEDOPTO hardware
- individual sensor models
- fan hardware

without rewriting the psychrometric controller.
