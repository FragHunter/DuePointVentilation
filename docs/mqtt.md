# MQTT contract

MQTT is the integration boundary between device/protocol adapters and the DuePointVentilation control logic.

## Normalized sensors

Topic:

`duepoint/site/<site>/sensor/<sensor-id>/state`

Payload:

```json
{
  "sensor_id": "aqara-room-a",
  "temperature_c": 18.2,
  "relative_humidity_pct": 72.4,
  "pressure_hpa": 1007.3,
  "battery_pct": 84,
  "timestamp_ms": 1790500000000
}
```

Raw Zigbee2MQTT topics remain outside the control core. Node-RED normalizes them first.

## Pair state

Topic:

`duepoint/site/<site>/pair/<pair-id>/state`

Example:

```json
{
  "pair_id": "cellar-pair-1",
  "phase": "PHASE_A",
  "reason": "OUTSIDE_AIR_DRIER",
  "ventilation_eligible": true,
  "delta_absolute_humidity_gm3": 2.14,
  "entered_at_ms": 1790500000000
}
```

## Logical fan targets

Topics:

- `duepoint/site/<site>/module/<module-id>/fan/intake/target`
- `duepoint/site/<site>/module/<module-id>/fan/exhaust/target`

Payload:

```json
{
  "percent": 65,
  "source": "pendulum-controller",
  "phase": "PHASE_A",
  "timestamp_ms": 1790500000000
}
```

The WLED/GLEDOPTO adapter translates this logical percentage into the concrete controller protocol.

## Safety rule

A module must never receive non-zero intake and exhaust targets at the same time during normal automatic operation.

During OFF, FAULT and switching dead-time, both targets are zero.

## Command freshness and reconnect safety

Logical actuator commands now carry:

- command_id
- generated_at_ms
- valid_until_ms
- transition sequence

The WLED/GLEDOPTO adapter must reject expired commands. Transient fan targets should not be retained in MQTT. On adapter/controller startup or reconnect, the safe default is all fans OFF until a fresh command is received.

## Airflow calibration

Equal PWM does not imply equal airflow. The controller therefore supports independent direction factors for:

- room A supply
- room A exhaust
- room B supply
- room B exhaust

These factors remain 1.0 until the bench tests provide measured balancing data.
