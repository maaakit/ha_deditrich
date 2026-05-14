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

bashio::log.info "Starting iSystem2MQTT..."
bashio::log.info "MQTT broker: ${MQTT_HOST}:${MQTT_PORT}"
bashio::log.info "Boiler model: ${MODEL}, serial: ${SERIAL}, poll interval: ${INTERVAL}s"

exec python3 /isystem-to-mqtt/bin/poll_isystem_mqtt.py \
    --user "${MQTT_USER}" \
    --password "${MQTT_PASSWORD}" \
    --interval "${INTERVAL}" \
    --log "${LOG_LEVEL}" \
    --model "${MODEL}" \
    --serial "${SERIAL}" \
    --deviceid "${DEVICE_ID}" \
    "${MQTT_HOST}"
