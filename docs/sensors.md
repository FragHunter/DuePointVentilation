# Sensor architecture

## Initial sensor choice

The initial environmental sensor is the **Aqara Temperature and Humidity Sensor T1**.

Reference model names used by the ecosystem include:

- Aqara model: **TH-S02D**
- Zigbee2MQTT device entry: **WSDCGQ12LM / TH-S02D**
- Wireless protocol: **Zigbee 3.0**
- Battery: **CR2032**

The sensor provides:

- temperature
- relative humidity
- atmospheric pressure

Zigbee2MQTT additionally exposes operational values such as battery state and voltage.

## Recommended integration path

```text
Aqara T1
   │
   │ Zigbee 3.0
   ▼
Zigbee coordinator
   │
   ▼
Zigbee2MQTT
   │
   │ MQTT
   ▼
Node-RED
   │
   ├── validation
   ├── calibration
   ├── dew-point calculation
   ├── absolute-humidity calculation
   └── ventilation decision
```

This avoids putting the ventilation logic into the Zigbee gateway. Zigbee2MQTT is used only as the hardware/protocol bridge; Node-RED owns the automation logic.

## Logical sensor model

Raw Zigbee2MQTT messages are normalized before they enter the controller.

Example normalized message:

```json
{
  "sensor_id": "cellar-east-inside",
  "temperature_c": 14.82,
  "relative_humidity_pct": 71.4,
  "pressure_hpa": 1008.2,
  "battery_pct": 87,
  "timestamp": "2026-09-27T09:00:00Z"
}
```

The controller must not depend directly on Zigbee2MQTT field names.

## Sensor roles

At minimum, one installation requires:

- **inside sensor**
- **outside reference sensor**

Optional later:

- cold-wall / surface temperature
- additional room sensors
- multiple outdoor reference sensors
- CO2 / VOC
- rainfall / wind

Example configuration:

```yaml
installation:
  id: cellar-east

  sensors:
    indoor:
      id: aqara-cellar-east
      role: indoor

    outdoor:
      id: aqara-outside-north
      role: outdoor
```

## Outdoor use

The Aqara T1 is treated as an indoor environmental sensor. If used as an outdoor reference, it must be installed in a suitable **ventilated weather shield** that protects it against direct rain, condensation and solar radiation while allowing representative ambient-air measurements.

Do not seal it into an airtight box; that would compromise humidity and temperature response.

## Validation and stale-data rules

Node-RED shall reject or inhibit automatic ventilation when required measurements are invalid or stale.

Initial validation rules:

- relative humidity: 0–100 %
- temperature: configurable plausible range
- timestamp required
- stale timeout configurable
- no automatic ventilation if indoor or outdoor reference is unavailable
- battery warnings are logged but do not immediately stop control while valid measurements continue

## Calibration

Multiple sensors should be compared side-by-side before deployment.

Store correction values separately from raw measurements:

```yaml
calibration:
  temperature_offset_c: 0.0
  humidity_offset_pct: 0.0
```

Raw values should still be retained for diagnostics.

## MQTT naming

Zigbee2MQTT topic names are considered an input interface only.

Normalized project topics:

```text
duepoint/site/<site>/sensor/<sensor-id>/state
```

Example:

```text
duepoint/site/home/sensor/aqara-cellar-east/state
```

## Sources

- Aqara Temperature and Humidity Sensor T1 specifications:
  https://www.aqara.com/en/temperature-and-humidity-sensor-t1/temperature-and-humidity-sensor-t1-specs
- Zigbee2MQTT device support:
  https://www.zigbee2mqtt.io/devices/WSDCGQ12LM.html
