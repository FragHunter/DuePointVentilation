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

## Physical fan-channel mapping

Logical room/direction targets remain the MQTT/control contract.

The GL-C-211WL adapter must not expose its three physical channels directly into psychrometric/FSM logic. A hardware-mapping layer translates logical roles to fan_1/fan_2/fan_3 only after the mechanical topology is explicitly configured and validated.

The logical mapping is resolved by Issue #14. The preferred V0.3 hardware map uses a supply bank (fan_1 + fan_2), an exhaust bank (fan_3), and two distinct full-area T-diverter units coupled by one logical servo route.


## Physical actuator command

The raw logical controller output must pass through the actuator interlock before
hardware-specific WLED/GPIO translation.

Suggested internal topic:

duepoint/site/<site>/pair/<pair-id>/actuator/target

The physical payload contains accepted/interlock_reason, command freshness
metadata, fan_1/fan_2/fan_3 percentages, the commanded/stable route, mechanism
coupled_dual_t_diverter, coupling single_servo_linkage and the two mechanical
unit IDs supply_t_diverter / exhaust_t_diverter.

While moving, expired, rejected or uncalibrated, all fan percentages are zero.

The hardware-specific WLED/GPIO adapter may command the servo route while fan
targets are zero, but it must not override the interlock's zero fan targets.

Do not retain non-zero physical actuator messages.
