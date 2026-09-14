# Changelog

## [0.1.6] - 2026-09-14

### Added
- Added Home Assistant MQTT Discovery `select` entities for selecting programs P1 through P4 for zone A and zone B

### Changed
- Home Assistant MQTT Discovery now publishes eight entities: six temperature controls and two program selectors
- Updated DHW day and night temperature controls to use a 40–60°C range
- Documented the new program selector entities and their MQTT topics

## [0.1.5] - 2026-09-14

### Added
- Added Home Assistant MQTT Discovery slider entities for day and night target temperatures of zones A, B and DHW

### Changed
- Added polling of DHW target registers required by the temperature discovery entities

## [0.1.4] - 2026-09-14

### Added
- Added MQTT write topics for DHW day and night target temperatures
- Added tests covering DHW temperature write registers for both supported boiler models

## [0.1.3] - 2026-09-05

### Added
- Added diagnostic Modbus writes through the `heating/diagnostic/write` MQTT topic
- Added support for writing one register or a consecutive range of registers using JSON payloads

### Security
- Validated diagnostic write addresses and values to the Modbus register range

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
