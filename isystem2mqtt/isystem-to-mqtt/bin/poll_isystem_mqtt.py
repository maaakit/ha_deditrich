#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import json
import logging
import time

try:
    import queue
except ImportError:
    import Queue as queue

import minimalmodbus
import paho.mqtt.client as mqtt

import isystem_to_mqtt.tables
import isystem_to_mqtt.isystem_modbus
import isystem_to_mqtt.mqtt_discovery
import isystem_to_mqtt.program_visualization

parser = argparse.ArgumentParser()
parser.add_argument("server", help="MQtt server to connect to.")
parser.add_argument("--user", help="MQtt username.")
parser.add_argument("--password", help="MQtt password.")
parser.add_argument("--interval", help="Check interval default 60s.", type=int, default=60)
parser.add_argument("--cacert", help="CA Certificate, default /etc/ssl/certs/ca-certificates.crt.",
                    default="/etc/ssl/certs/ca-certificates.crt")
parser.add_argument("--serial", help="Serial interface, default /dev/ttyUSB0",
                    default="/dev/ttyUSB0")
parser.add_argument("--deviceid", help="Modbus device id, default 10",
                    type=int, default=10)
parser.add_argument("--log", help="Logging level, default INFO",
                    default="INFO")
parser.add_argument("--bimaster", help="bi-master mode (5s for peer, 5s for us)",
                    action="store_true")
parser.add_argument("--model", help="boiler model",
                    default="modulens-o")
parser.add_argument("--lang", help="language in mqtt message",
                    default="en")
parser.add_argument("--custom-css-file",
                    help="optional CSS file for program SVG images",
                    default="")
# handle no sll.PROTOCOL_TLSv1_2
try:
    import ssl
    parser.add_argument("--tls12", help="use TLS 1.2", dest="tls",
                        action="store_const", const=ssl.PROTOCOL_TLSv1_2)
except:
    pass

args = parser.parse_args()

# Convert to upper case to allow the user to
# specify --log=DEBUG or --log=debug
numeric_level = getattr(logging, args.log.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError("Invalid log level: {0}".format(args.log))
logging.basicConfig(level=numeric_level,
                    format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s",
                    datefmt="%H:%M:%S")

_LOGGER = logging.getLogger(__name__)


(READ_TABLE, WRITE_TABLE, READ_ZONES) = isystem_to_mqtt.tables.get_tables_translated(args.model, args.lang)
custom_css = isystem_to_mqtt.program_visualization.load_custom_css(
    args.custom_css_file)


# Initialisation of mqtt client
base_topic = "heating/"
diagnostic_write_topic = base_topic + "diagnostic/write"

port_mqtt = 1883
client = mqtt.Client()
# client.on_log = on_log
if args.user:
    _LOGGER.debug("Authenticate with user %s", args.user)
    client.username_pw_set(args.user, args.password)
try:
    if args.tls:
        _LOGGER.debug("Set TLS mode.")
        client.tls_set(args.cacert, tls_version=args.tls)
        port_mqtt = 8883
except:
    pass

client.will_set(base_topic + "reading", "OFF", 1, True)

write_queue = queue.Queue()

def on_message(the_client, userdata, message):
    _LOGGER.debug(message)
    write_queue.put(message)

client.on_message = on_message

subscribe_list = [(base_topic + name, 0) for name in WRITE_TABLE.keys()]
subscribe_list.append((diagnostic_write_topic, 0))

program_image_definitions = {
    126: ("zone-a", "Zone A"),
    147: ("zone-b", "Zone B"),
    168: ("zone-c", "Zone C"),
    189: ("dhw", "DHW"),
}
last_program_images = {}

def on_connect(the_client, userdata, flags, rc):
    _LOGGER.debug("ON CONNECT")
    if rc == mqtt.CONNACK_ACCEPTED:
        the_client.subscribe(subscribe_list)
        discovery_configs = (
            isystem_to_mqtt.mqtt_discovery.temperature_number_configs(
                base_topic, args.model)
            + isystem_to_mqtt.mqtt_discovery.program_select_configs(
                base_topic, args.model)
            + isystem_to_mqtt.mqtt_discovery.program_image_configs(
                base_topic, args.model))
        for discovery_topic, discovery_payload in discovery_configs:
            result = the_client.publish(discovery_topic, discovery_payload, 1, True)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                _LOGGER.warning("Failed to publish MQTT Discovery config to %s: %s",
                                discovery_topic, result.rc)
        client.publish(base_topic + "reading", "ON", 1, True)

client.on_connect = on_connect

client.connect(args.server, port_mqtt)
client.loop_start()

# Initialisation of Modbus
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True
instrument = isystem_to_mqtt.isystem_modbus.ISystemInstrument(args.serial,
                                                              args.deviceid,
                                                              args.bimaster)
instrument.debug = False   # True or False


RETRY_COUNT = 3
RETRY_DELAY = 1


def read_zone(base_address, number_of_value):
    """ Read a MODBUS table zone and send the value to MQTT. """
    for attempt in range(RETRY_COUNT + 1):
        try:
            raw_values = instrument.read_registers(base_address, number_of_value)
        except minimalmodbus.NoResponseError:
            if attempt < RETRY_COUNT:
                _LOGGER.error("I/O error reading modbus registers, retrying in %ds (attempt %d/%d)...",
                              RETRY_DELAY, attempt + 1, RETRY_COUNT, exc_info=True)
                time.sleep(RETRY_DELAY)
                continue
            _LOGGER.error("I/O error reading modbus registers after %d retries, skipping cycle.",
                          RETRY_COUNT, exc_info=True)
            return
        except EnvironmentError:
            _LOGGER.error("I/O error", exc_info=True)
            return
        except ValueError:
            _LOGGER.error("Value error", exc_info=True)
            return
        else:
            for index in range(0, number_of_value):
                address = base_address + index
                tag_definition = READ_TABLE.get(address)
                if tag_definition:
                    value = tag_definition.publish(
                        client, base_topic, raw_values, index)
                    image_definition = program_image_definitions.get(address)
                    if image_definition:
                        zone_id, zone_name = image_definition
                        try:
                            schedule = json.loads(value)
                        except (TypeError, ValueError) as error:
                            _LOGGER.error(
                                "Invalid schedule for %s: %s",
                                zone_id, error)
                            continue
                        image = isystem_to_mqtt.program_visualization.render_schedule_svg(
                            schedule, zone_name, custom_css=custom_css)
                        if image != last_program_images.get(zone_id):
                            image_topic = base_topic + zone_id + "/program/image"
                            result = client.publish(
                                image_topic, image, retain=True)
                            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                                _LOGGER.warning(
                                    "Failed to publish program image to %s: %s",
                                    image_topic, result.rc)
                            else:
                                last_program_images[zone_id] = image
            return

def write_value(message):
    """ Write a value receive from MQTT to MODBUS """
    topic_name = message.topic[len(base_topic):] if message.topic.startswith(base_topic) else message.topic
    tag_definition = WRITE_TABLE.get(topic_name)
    if tag_definition:
        string_value = message.payload.decode("utf-8")
        _LOGGER.debug("write value %s : %s", topic_name, string_value)
        tag_definition.write(instrument, string_value)


def write_diagnostic_value(message):
    """Write an arbitrary single Modbus register from diagnostic JSON."""
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        address = payload["adr"]
        value = payload["val"]
        if isinstance(address, bool) or not isinstance(address, int):
            raise ValueError("adr must be an integer")
        if isinstance(value, int) and not isinstance(value, bool):
            values = [value]
        elif isinstance(value, list) and value:
            values = value
        else:
            raise ValueError("val must be an integer or a non-empty array of integers")
        if any(isinstance(item, bool) or not isinstance(item, int) or
               not 0 <= item <= 0xFFFF for item in values):
            raise ValueError("val items must be integers between 0 and 65535")
        if not 0 <= address <= 0xFFFF or address + len(values) - 1 > 0xFFFF:
            raise ValueError("register range must be between 0 and 65535")
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        _LOGGER.warning("Invalid diagnostic write payload: %s (%s)", message.payload, error)
        return

    _LOGGER.warning("Diagnostic write: address %d = %s", address, values)
    instrument.write_registers(address, values)


instrument.wait_time_slot()

# Main loop
while True:
    # update watchdog (reset by will)
    client.publish(base_topic + "reading", "ON", 1, True)
    # The total read time must be under the time slot duration
    start_time = time.time()
    for zone in READ_ZONES:
        if zone[1] == 0:
            instrument.wait_time_slot()
        else:
            read_zone(zone[0], zone[1])

    duration = time.time() - start_time
    _LOGGER.debug("Read take %1.3fs", duration)
    if duration > isystem_to_mqtt.isystem_modbus.MAXIMUM_OPERATION:
        _LOGGER.warning("Read take too long, wait_time_slot must be added between read_zone.")

    # Traitement de toute les ecritures ou attente de l'intervale
    try:
        waittime = args.interval
        while True:
            writeelement = write_queue.get(timeout=waittime)

            instrument.wait_time_slot()
            if writeelement.topic == diagnostic_write_topic:
                write_diagnostic_value(writeelement)
            else:
                write_value(writeelement)
            waittime = 0
    except queue.Empty:
        # no more write, continue to read.
        instrument.wait_time_slot()
        continue
