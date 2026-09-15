# iSystem to MQTT - Home Assistant Add-on

Bridges an **iSystem / Deditrich** central heating boiler to MQTT, enabling integration with Home Assistant.

Communication with the boiler uses **Modbus RS485** via a USB-RS485 adapter (e.g. `/dev/ttyUSB0`).

## Requirements

- USB to RS485 adapter connected to your Home Assistant host
- MQTT broker (e.g. Mosquitto add-on)
- iSystem boiler with Modbus interface (tested with `modulens-g` model)

## Installation

1. In Home Assistant go to **Settings → Add-ons → Add-on Store**
2. Click the menu (⋮) and select **Repositories**
3. Add this repository URL: `https://github.com/markitsoft/ha_deditrich`
4. Find **iSystem to MQTT** in the add-on list and install it

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `mqtt_host` | `core-mosquitto` | MQTT broker hostname or IP |
| `mqtt_port` | `1883` | MQTT broker port |
| `mqtt_user` | `homeassistant` | MQTT username |
| `mqtt_password` | `` | MQTT password |
| `model` | `modulens-g` | Boiler model: `modulens-o` or `modulens-g` |
| `interval` | `15` | Polling interval in seconds |
| `serial` | `/dev/ttyUSB0` | Serial device path |
| `device_id` | `10` | Modbus device ID |
| `log_level` | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `custom_css_file` | `` | Optional CSS file used to style generated program SVG images |

The optional `custom_css_file` path is read from the Home Assistant `/config`
directory, for example `/config/isystem2mqtt/program.css`. The file is
embedded into generated SVG images. Only the documented renderer classes
should be customized:

```css
.program-background {
  fill: #101820;
}

.program-grid {
  stroke: #38434d;
}

.program-period {
  fill: #ff9800;
}

.program-day-label,
.program-time-label {
  fill: #ffffff;
}
```

The CSS file must contain styles only. JavaScript, external resources,
`@import`, and `url(...)` are not supported.

## MQTT Topics

Data is published under the `heating/` topic prefix. Examples:
- `heating/boiler/version`
- `heating/outside/temperature`
- `heating/zone-a/temperature`
- `heating/zone-a/mode`
- `heating/dhw/day-temperature/SET` — set DHW day target temperature
- `heating/dhw/night-temperature/SET` — set DHW night target temperature
- `heating/reading` — watchdog: `ON` when running, `OFF` on disconnect

The add-on also publishes Home Assistant MQTT Discovery configurations for
slider entities controlling the day and night target temperatures of zone A,
zone B and DHW, plus `select` entities for choosing programs P1 through P4
for zone A and zone B. The program selectors use the existing
`heating/zone-a/program/SET` and `heating/zone-b/program/SET` topics.

The add-on also publishes three `image` entities containing the currently
active schedule for zones A, B and C:

```text
heating/zone-a/program/image
heating/zone-b/program/image
heating/zone-c/program/image
```

The images are regenerated when the corresponding active schedule changes.

For diagnostic writes, publish a non-retained JSON message to
`heating/diagnostic/write`, for example:

```json
{"adr": 650, "val": 210}
```

`adr` must be an integer from 0 to 65535. `val` can be one integer or an
array of integers, for example `{"adr": 650, "val": [210, 220, 230]}`;
the array is written to consecutive Modbus registers. All values must be
between 0 and 65535. This topic bypasses the normal named-register
validation; use it only for testing and with care.

## Credits

Based on [isystem-to-mqtt](https://github.com/ngraziano/isystem-to-mqtt) by Nicolas Graziano.
