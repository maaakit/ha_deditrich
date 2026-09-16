"""Render weekly heating schedules as standalone SVG images."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import logging
import os


_LOGGER = logging.getLogger(__name__)


DEFAULT_CSS = """
.program-background { fill: #111111; }
.program-grid { stroke: #292929; stroke-width: 1; }
.program-row { stroke: #202020; }
.program-row-even { fill: #0f0f0f; }
.program-row-odd { fill: #111111; }
.program-period { fill: #c8872a; stroke: #dfa044; stroke-width: 1; }
.program-day-label {
  fill: #eeeeee;
  font-family: sans-serif;
  font-size: 28px;
}
.program-time-label {
  fill: #9a9ba5;
  font-family: sans-serif;
  font-size: 24px;
}
"""
MAX_CUSTOM_CSS_SIZE = 64 * 1024

DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday")
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 390
LEFT_MARGIN = 125
RIGHT_MARGIN = 70
TOP_MARGIN = 58
ROW_HEIGHT = 40
TIMELINE_WIDTH = IMAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


def load_custom_css(path):
    """Load a validated CSS override file.

    Supported SVG classes are ``program-background``, ``program-grid``,
    ``program-row``, ``program-period``, ``program-day-label``, and
    ``program-time-label``.
    """
    if not path:
        return ""
    try:
        with open(path, "r") as css_file:
            css = css_file.read()
    except FileNotFoundError:
        _LOGGER.warning("Custom CSS file not found: %s; using default CSS", path)
        return ""
    if len(css) > MAX_CUSTOM_CSS_SIZE:
        raise ValueError("custom CSS file is larger than 64 KiB")
    lowered = css.lower()
    for forbidden in ("<", ">", "@import", "url(", "<script", "javascript:"):
        if forbidden in lowered:
            raise ValueError("custom CSS contains unsupported content: {}".format(
                forbidden))
    return css


def _minutes(value):
    """Return a timedelta or HH:MM[:SS] value as minutes from midnight."""
    if isinstance(value, datetime.timedelta):
        return value.total_seconds() / 60
    if isinstance(value, str):
        parts = value.split(":")
        if len(parts) not in (2, 3):
            raise ValueError("time must use HH:MM or HH:MM:SS format")
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) if len(parts) == 3 else 0
        return hours * 60 + minutes + seconds / 60
    raise TypeError("schedule times must be timedelta or time strings")


def render_schedule_svg(schedule, zone_name, program_number=None,
                        custom_css=""):
    """Return an SVG visualization for a seven-day schedule.

    ``schedule`` is a mapping from day number (0-6) to intervals. Each
    interval is a ``(start, end)`` pair using timedeltas or time strings.

    Supported CSS classes are ``program-background``, ``program-grid``,
    ``program-row``, ``program-period``, ``program-day-label``, and
    ``program-time-label``.
    """
    if not hasattr(schedule, "items"):
        raise TypeError("schedule must be a mapping")

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="{}" height="{}" '
        'viewBox="0 0 {} {}">'.format(
            IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT),
        "<style>{}{}</style>".format(DEFAULT_CSS, custom_css),
        '<rect class="program-background" width="100%" height="100%"/>',
    ]

    for hour in range(0, 25):
        x = LEFT_MARGIN + TIMELINE_WIDTH * hour / 24
        if hour % 4 == 0:
            parts.append(
                '<text x="{0:.1f}" y="{1}" text-anchor="middle" '
                'class="program-time-label">{2:02d}:00</text>'.format(
                    x, TOP_MARGIN - 18, hour))

    for day in range(7):
        y = TOP_MARGIN + day * ROW_HEIGHT
        parts.append(
            '<text x="{}" y="{}" text-anchor="end" dominant-baseline="middle" '
            'class="program-day-label">{}</text>'.format(
                LEFT_MARGIN - 12, y + ROW_HEIGHT / 2, DAY_NAMES[day]))
        parts.append(
            '<rect class="program-row {}" x="{}" y="{}" width="{}" height="{}"/>'.format(
                "program-row-even" if day % 2 == 0 else "program-row-odd",
                LEFT_MARGIN, y, TIMELINE_WIDTH, ROW_HEIGHT,
            ))

        intervals = schedule.get(day, schedule.get(str(day), []))
        for interval in intervals:
            if len(interval) != 2:
                raise ValueError("each schedule interval must contain two times")
            start = max(0, min(1440, _minutes(interval[0])))
            end = max(0, min(1440, _minutes(interval[1])))
            if end <= start:
                continue
            x = LEFT_MARGIN + TIMELINE_WIDTH * start / 1440
            width = TIMELINE_WIDTH * (end - start) / 1440
            parts.append(
                '<rect class="program-period" x="{:.1f}" y="{:.1f}" '
                'width="{:.1f}" height="{}" rx="4"/>'.format(
                    x, y + 5, width, ROW_HEIGHT - 10))

    for hour in range(0, 25):
        x = LEFT_MARGIN + TIMELINE_WIDTH * hour / 24
        parts.append(
            '<line class="program-grid" x1="{0:.1f}" y1="{1}" '
            'x2="{0:.1f}" y2="{2}"/>'.format(
                x,
                TOP_MARGIN,
                TOP_MARGIN + ROW_HEIGHT * 7,
            ))

    parts.append("</svg>")
    return "\n".join(parts)


def write_schedule_svg(schedule, zone_name, output_path, program_number=None,
                       custom_css=""):
    """Render a schedule and write it to an SVG file."""
    output_directory = os.path.dirname(output_path)
    if output_directory and not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    with open(output_path, "w") as output_file:
        output_file.write(render_schedule_svg(
            schedule, zone_name, program_number=program_number,
            custom_css=custom_css))


def write_zone_schedule_images(schedules, output_directory, program_numbers=None,
                               custom_css_file=""):
    """Write one visualization for each zone in ``schedules``.

    ``schedules`` maps zone identifiers such as ``zone-a`` to weekly
    schedules. The returned mapping contains the generated file paths.
    """
    if program_numbers is None:
        program_numbers = {}
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    custom_css = load_custom_css(custom_css_file)

    paths = {}
    for zone_id, schedule in sorted(schedules.items()):
        zone_name = zone_id.replace("-", " ").title()
        output_path = os.path.join(output_directory, "{}-program.svg".format(zone_id))
        write_schedule_svg(
            schedule,
            zone_name,
            output_path,
            program_number=program_numbers.get(zone_id),
            custom_css=custom_css)
        paths[zone_id] = output_path
    return paths
