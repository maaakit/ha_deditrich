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
zone B and DHW. The selected heating program is published for zone A, B and C,
but program selection is read-only through Modbus. P1-P3 weekly schedules are
not exposed by the iSystem Modbus interface; the available heating schedules
are P4 for zones A, B and C.

The add-on publishes the following weekly schedule topics:

```text
heating/zone-a/schedule-p4
heating/zone-b/schedule-p4
heating/zone-c/schedule-p4
heating/dhw/schedule
```

The zone topics contain the stored P4 schedules. `heating/dhw/schedule`
contains the domestic hot-water (DHW/CWU) schedule. These schedules are
currently read-only in the add-on; no schedule-writing MQTT topic is
implemented. Writing the DHW/CWU schedule has been observed to work on the
tested installation, but it is not yet implemented or supported here.

The add-on also publishes four `image` entities containing these schedules:

```text
heating/zone-a/program/image
heating/zone-b/program/image
heating/zone-c/program/image
heating/dhw/program/image
```

The images are regenerated when the corresponding read schedule changes.

The selected program topics are read-only status topics:

```text
heating/zone-a/program
heating/zone-b/program
heating/zone-c/program
```

Their values are numeric (`0` to `3`), corresponding to P1 through P4.
The add-on does not use program selection to retrieve P1-P3 schedules.

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
