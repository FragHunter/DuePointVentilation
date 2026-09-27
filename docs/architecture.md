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
       ┌────────────────────────────────────┐
       │ paired pendulum ventilation group  │
       └───────────────┬────────────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
     Room A module            Room B module
   intake + exhaust         intake + exhaust
          fan pair                 fan pair
           │                       │
           ▼                       ▼
     regenerative             regenerative
     heat-store core          heat-store core
           │                       │
           ▼                       ▼
        outside                  outside

Phase 1: Room A SUPPLY, Room B EXHAUST
Phase 2: Room A EXHAUST, Room B SUPPLY

Future actuator path:
Node-RED → servo adapter → directional/bypass dampers
```

## Installation and pair model

One physical module belongs to one room. Two modules in two rooms form one **pendulum pair**.

Each module has two directional fans as already planned:

- intake fan for SUPPLY
- exhaust fan for EXHAUST

Only the fan required for the active direction is commanded during normal pendulum operation.

```yaml
pendulum_pair:
  id: cellar-pair-1
  phase_time_s: 60
  switch_deadtime_s: 3

  modules:
    - id: cellar-room-a
      sensor: aqara-cellar-room-a
      outdoor_sensor: aqara-outside-north
      intake_fan:
        controller: wled-room-a
        channel: 0
      exhaust_fan:
        controller: wled-room-a
        channel: 1

    - id: cellar-room-b
      sensor: aqara-cellar-room-b
      outdoor_sensor: aqara-outside-north
      intake_fan:
        controller: wled-room-b
        channel: 0
      exhaust_fan:
        controller: wled-room-b
        channel: 1
```

Outdoor sensors may be shared between both rooms and additional pairs.

The exact phase duration remains configurable and must be tuned from heat-storage performance, airflow and comfort measurements.

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

The controller emits pair-aware logical targets independent of hardware.

Example phase 1:

```json
{
  "pair_id": "cellar-pair-1",
  "state": "PENDULUM_PHASE_A",
  "reason": "OUTSIDE_AIR_DRIER",
  "modules": {
    "cellar-room-a": {"mode": "SUPPLY", "intake_pct": 65, "exhaust_pct": 0},
    "cellar-room-b": {"mode": "EXHAUST", "intake_pct": 0, "exhaust_pct": 65}
  }
}
```

After the configured phase time and a short dead-time, the roles swap.

The WLED adapter maps these logical targets to the actual GLEDOPTO controllers.

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

## Paired pendulum ventilation and heat recovery

The primary operating mode uses **two modules in two rooms**.

```text
PHASE A
Room A: outside ──► core ──► room      (SUPPLY)
Room B: room ─────► core ──► outside   (EXHAUST)

          wait / switch dead-time

PHASE B
Room A: room ─────► core ──► outside   (EXHAUST)
Room B: outside ──► core ──► room      (SUPPLY)
```

This keeps the pair approximately volume-balanced while each local heat-storage core alternately:

1. absorbs heat from outgoing room air, then
2. releases that heat into incoming outside air.

This is a **regenerative** heat-recovery concept, not a simultaneous two-stream plate exchanger.

Node-RED owns the pair phase state and must switch both rooms atomically enough that we do not intentionally leave both modules in SUPPLY or both in EXHAUST.

Required control concepts:

- configurable phase duration
- short all-off dead-time during direction changes
- paired phase synchronization
- safe recovery after Node-RED/controller restart
- degraded/fault mode if one module is unavailable
- explicit manual test mode
- optional asymmetric PWM only when intentionally configured

A pressure-balanced pair still needs a real air-transfer path through the building/rooms. Closed doors and highly sealed rooms can change the actual pressure and airflow behavior and must be tested.

The mechanical design must also ensure that the inactive fan does not create an unacceptable bypass or pressure restriction. This depends on whether the two directional fans share one duct/core or use separate routed paths and is a key CAD decision.

Condensate handling, pressure drop, thermal-storage performance and frost behavior remain explicit design/test items.

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
