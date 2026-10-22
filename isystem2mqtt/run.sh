#!/usr/bin/with-contenv bashio
# ==============================================================================
# iSystem to MQTT - Start script
# Reads configuration options and launches the poll_isystem_mqtt.py script
# ==============================================================================

MQTT_HOST=$(bashio::config 'mqtt_host')
MQTT_PORT=$(bashio::config 'mqtt_port')
MQTT_USER=$(bashio::config 'mqtt_user')
MQTT_PASSWORD=$(bashio::config 'mqtt_password')
MODEL=$(bashio::config 'model')
INTERVAL=$(bashio::config 'interval')
SERIAL=$(bashio::config 'serial')
DEVICE_ID=$(bashio::config 'device_id')
LOG_LEVEL=$(bashio::config 'log_level')
PERSISTENT_LOGGING=$(bashio::config 'persistent_logging')
LOG_RETENTION_DAYS=$(bashio::config 'log_retention_days')
CUSTOM_CSS_FILE=$(bashio::config 'custom_css_file')

bashio::log.info "Starting iSystem2MQTT..."
bashio::log.info "MQTT broker: ${MQTT_HOST}:${MQTT_PORT}"
bashio::log.info "Boiler model: ${MODEL}, serial: ${SERIAL}, poll interval: ${INTERVAL}s"

PERSISTENT_LOGGING_ARGS=()
if [ "${PERSISTENT_LOGGING}" = "true" ]; then
    PERSISTENT_LOGGING_ARGS+=(--persistent-logging)
    PERSISTENT_LOGGING_ARGS+=(--log-retention-days "${LOG_RETENTION_DAYS}")
fi

exec python3 /isystem-to-mqtt/bin/poll_isystem_mqtt.py \
    --user "${MQTT_USER}" \
    --password "${MQTT_PASSWORD}" \
    --interval "${INTERVAL}" \
    --log "${LOG_LEVEL}" \
    "${PERSISTENT_LOGGING_ARGS[@]}" \
    --model "${MODEL}" \
    --serial "${SERIAL}" \
    --deviceid "${DEVICE_ID}" \
    --custom-css-file "${CUSTOM_CSS_FILE}" \
    "${MQTT_HOST}"
