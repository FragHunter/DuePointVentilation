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

## Alternative Zigbee temperature/humidity sensors

The controller is intentionally sensor-agnostic. The following devices are good candidates for evaluation alongside the Aqara T1.

### SONOFF SNZB-02WD — preferred outdoor candidate

- Zigbee 3.0
- temperature + relative humidity
- IP65 enclosure
- specified range: -20 °C to 60 °C and 0–100 % RH
- specified accuracy: ±0.2 °C / ±2 % RH
- supported by Zigbee2MQTT
- CR2477 battery
- exposes temperature/humidity calibration through Zigbee2MQTT

This is the most interesting candidate for the **outdoor reference sensor**, because it is designed for outdoor/very humid environments and removes the need to rely on an indoor-only sensor in a custom weatherproof enclosure. It still should be positioned so that direct solar radiation does not bias the temperature measurement.

### SONOFF SNZB-02P — strong indoor candidate

- Zigbee 3.0
- temperature + relative humidity
- specified accuracy: ±0.2 °C / ±2 % RH
- working range: -10 °C to 60 °C, 5–95 % RH, non-condensing
- supported by Zigbee2MQTT
- CR2477 battery
- manufacturer specifies up to roughly four years battery life
- no display

Good candidate for basements and other indoor zones where no local display is needed.

### SONOFF SNZB-02D — indoor sensor with display

- Zigbee 3.0
- temperature + relative humidity
- LCD display
- specified accuracy: ±0.2 °C / ±2 % RH
- supported by Zigbee2MQTT
- CR2450 battery

Useful where the current local reading should also be visible without opening Grafana/Home Assistant.

### Third Reality Temperature & Humidity Sensor Lite (3RTHS0224Z)

- Zigbee 3.0
- temperature + relative humidity
- 2 × AAA batteries
- manufacturer specifies ±0.3 °C / ±2 % RH for the current Lite generation
- supported by Zigbee2MQTT
- indoor use

AAA cells can be attractive for long-term maintenance compared with coin cells.

### Older Aqara WSDCGQ11LM

- temperature + relative humidity + air pressure
- CR2032
- supported by Zigbee2MQTT

This model is still usable, but Zigbee2MQTT documents that some Xiaomi/Aqara devices do not fully comply with the Zigbee standard and can occasionally disconnect from some networks. Prefer the T1 or a SONOFF alternative for new installations unless there is a specific reason to use the older model.

### Generic Tuya TS0201 devices

Many inexpensive Zigbee temperature/humidity sensors use the TS0201 family and are supported by Zigbee2MQTT. They should be considered **secondary/test candidates**, because hardware and firmware can vary between white-label versions. Zigbee2MQTT currently also warns against a firmware update for one TS0201 variant because it can brick that device.

## Initial project sensor matrix

| Role | Preferred candidate | Alternative |
| --- | --- | --- |
| Indoor zone | Aqara T1 | SONOFF SNZB-02P |
| Indoor with display | SONOFF SNZB-02D | Third Reality 3RTHS24BZ / Lite |
| Outdoor reference | SONOFF SNZB-02WD | Aqara T1 in ventilated weather/radiation shield |
| Cheap lab/test node | SONOFF SNZB-02P | selected TS0201 variant |
| Pressure required | Aqara T1 / WSDCGQ11LM | separate pressure sensor |

For dew-point control, **temperature and relative humidity accuracy and repeatability matter more than brand**. We should therefore compare several units side-by-side before installation and store per-sensor calibration offsets.


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
