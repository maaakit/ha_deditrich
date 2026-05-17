# Changelog

## [0.1.2] - 2026-05-17

### Changed
- Improved error handling for Modbus I/O errors: log at ERROR level, retry up to 3 times with 1s delay, then continue to next cycle instead of exiting
- Added DEBUG log on MQTT publish (only when value changes)
- Log format now includes timestamp (HH:MM:SS.mmm)

## [0.1.0] - 2026-05-14

### Added
- Initial release of iSystem to MQTT Home Assistant add-on
- Support for iSystem boiler models: `modulens-o`, `modulens-g`
- Configurable MQTT broker, credentials, polling interval, serial port and Modbus device ID
- USB-RS485 device passthrough (`/dev/ttyUSB0`)
- Watchdog topic `heating/reading` (ON/OFF)
