"""Home Assistant MQTT Discovery configuration."""

import json


def temperature_number_configs(base_topic, model):
    """Return MQTT Discovery configs for temperature setpoint sliders."""
    definitions = (
        ("zone_a_day", "Zone A day temperature",
         "zone-a/day-target-temperature",
         "zone-a/day-target-temperature/SET", 15, 25),
        ("zone_a_night", "Zone A night temperature",
         "zone-a/night-target-temperature",
         "zone-a/night-target-temperature/SET", 15, 25),
        ("zone_b_day", "Zone B day temperature",
         "zone-b/day-target-temperature",
         "zone-b/day-target-temperature/SET", 15, 25),
        ("zone_b_night", "Zone B night temperature",
         "zone-b/night-target-temperature",
         "zone-b/night-target-temperature/SET", 15, 25),
        ("dhw_day", "DHW day temperature",
         "dhw/day-target-temperature",
         "dhw/day-temperature/SET", 40, 60),
        ("dhw_night", "DHW night temperature",
         "dhw/night-target-temperature",
         "dhw/night-temperature/SET", 40, 60),
    )
    device = {
        "identifiers": ["isystem2mqtt"],
        "name": "iSystem / DeDietrich",
        "manufacturer": "DeDietrich",
        "model": model,
    }
    configs = []
    for entity_id, name, state_suffix, command_suffix, minimum, maximum in definitions:
        unique_id = "isystem2mqtt_{}_temperature".format(entity_id)
        payload = {
            "name": name,
            "unique_id": unique_id,
            "command_topic": base_topic + command_suffix,
            "state_topic": base_topic + state_suffix,
            "availability_topic": base_topic + "reading",
            "payload_available": "ON",
            "payload_not_available": "OFF",
            "min": minimum,
            "max": maximum,
            "step": 1,
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "mode": "slider",
            "retain": False,
            "device": device,
        }
        discovery_topic = "homeassistant/number/{}/config".format(unique_id)
        configs.append((discovery_topic, json.dumps(payload)))
    return configs


def program_select_configs(base_topic, model):
    """Return MQTT Discovery configs for zone program selectors."""
    definitions = (
        ("zone_a", "Zone A program", "zone-a/program"),
        ("zone_b", "Zone B program", "zone-b/program"),
    )
    device = {
        "identifiers": ["isystem2mqtt"],
        "name": "iSystem / DeDietrich",
        "manufacturer": "DeDietrich",
        "model": model,
    }
    configs = []
    for zone_id, name, state_suffix in definitions:
        unique_id = "isystem2mqtt_{}_program".format(zone_id)
        payload = {
            "name": name,
            "unique_id": unique_id,
            "command_topic": base_topic + state_suffix + "/SET",
            "state_topic": base_topic + state_suffix,
            "availability_topic": base_topic + "reading",
            "payload_available": "ON",
            "payload_not_available": "OFF",
            "options": ["P1", "P2", "P3", "P4"],
            "command_template": "{{ ['P1', 'P2', 'P3', 'P4'].index(value) }}",
            "value_template": "P{{ value | int + 1 }}",
            "retain": False,
            "device": device,
        }
        discovery_topic = "homeassistant/select/{}/config".format(unique_id)
        configs.append((discovery_topic, json.dumps(payload)))
    return configs


def program_image_configs(base_topic, model):
    """Return MQTT Discovery configs for P4 program images."""
    definitions = (
        ("zone_a", "Zone A program P4", "zone-a/program/image"),
        ("zone_b", "Zone B program P4", "zone-b/program/image"),
        ("zone_c", "Zone C program P4", "zone-c/program/image"),
        ("dhw", "DHW schedule", "dhw/program/image"),
    )
    device = {
        "identifiers": ["isystem2mqtt"],
        "name": "iSystem / DeDietrich",
        "manufacturer": "DeDietrich",
        "model": model,
    }
    configs = []
    for entity_id, name, image_suffix in definitions:
        unique_id = "isystem2mqtt_{}_program_image".format(entity_id)
        payload = {
            "name": name,
            "unique_id": unique_id,
            "image_topic": base_topic + image_suffix,
            "content_type": "image/svg+xml",
            "availability_topic": base_topic + "reading",
            "payload_available": "ON",
            "payload_not_available": "OFF",
            "device": device,
        }
        discovery_topic = "homeassistant/image/{}/config".format(unique_id)
        configs.append((discovery_topic, json.dumps(payload)))
    return configs
