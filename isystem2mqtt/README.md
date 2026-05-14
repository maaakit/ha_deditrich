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

## MQTT Topics

Data is published under the `heating/` topic prefix. Examples:
- `heating/boiler/version`
- `heating/outside/temperature`
- `heating/zone-a/temperature`
- `heating/zone-a/mode`
- `heating/reading` — watchdog: `ON` when running, `OFF` on disconnect

## Credits

Based on [isystem-to-mqtt](https://github.com/ngraziano/isystem-to-mqtt) by Nicolas Graziano.
