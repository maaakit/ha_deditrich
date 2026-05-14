# Changelog

## [0.1.0] - 2026-05-14

### Added
- Initial release of iSystem to MQTT Home Assistant add-on
- Support for iSystem boiler models: `modulens-o`, `modulens-g`
- Configurable MQTT broker, credentials, polling interval, serial port and Modbus device ID
- USB-RS485 device passthrough (`/dev/ttyUSB0`)
- Watchdog topic `heating/reading` (ON/OFF)
