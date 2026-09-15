"""Tests and visual artifacts for weekly program rendering."""

from __future__ import absolute_import
from __future__ import print_function

import datetime
import os
import tempfile
import unittest

from .. import program_visualization


def _hours(start, end):
    return (datetime.timedelta(hours=start),
            datetime.timedelta(hours=end))


class TestProgramVisualization(unittest.TestCase):
    """Generate representative zone A-C schedule images."""

    def test_write_zone_program_images(self):
        schedules = {
            "zone-a": {
                0: [_hours(6, 9), _hours(16, 22)],
                1: [_hours(6, 9), _hours(16, 22)],
                2: [_hours(6, 9), _hours(16, 22)],
                3: [_hours(6, 9), _hours(16, 22)],
                4: [_hours(6, 9), _hours(16, 22)],
                5: [_hours(8, 23)],
                6: [_hours(8, 22)],
            },
            "zone-b": {
                0: [_hours(5, 8), _hours(15, 21)],
                1: [_hours(5, 8), _hours(15, 21)],
                2: [_hours(5, 8), _hours(15, 21)],
                3: [_hours(5, 8), _hours(15, 21)],
                4: [_hours(5, 8), _hours(15, 21)],
                5: [_hours(7, 22)],
                6: [_hours(7, 22)],
            },
            "zone-c": {
                0: [_hours(7, 20)],
                1: [_hours(7, 20)],
                2: [_hours(7, 20)],
                3: [_hours(7, 20)],
                4: [_hours(7, 20)],
                5: [],
                6: [],
            },
        }
        output_directory = os.environ.get(
            "PROGRAM_IMAGE_OUTPUT",
            os.path.join(os.path.dirname(__file__), "generated_program_images"))

        paths = program_visualization.write_zone_schedule_images(
            schedules,
            output_directory,
            program_numbers={"zone-a": 1, "zone-b": 2, "zone-c": 3})

        self.assertEqual(["zone-a", "zone-b", "zone-c"], sorted(paths.keys()))
        for zone_id, path in paths.items():
            self.assertTrue(os.path.isfile(path))
            with open(path, "r") as image_file:
                image = image_file.read()
            self.assertIn("<svg", image)
            self.assertNotIn("Heating period", image)
            self.assertNotIn("Zone", image)
            self.assertIn(">04:00</text>", image)
            self.assertIn(">08:00</text>", image)
            self.assertEqual(25, image.count('<line class="program-grid"'))

    def test_custom_css_file_is_embedded(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".css",
                                         delete=False) as css_file:
            css_file.write(".program-period { fill: #00ff00; }")
            css_path = css_file.name
        try:
            css = program_visualization.load_custom_css(css_path)
            image = program_visualization.render_schedule_svg(
                {0: [_hours(8, 10)]},
                "Zone A",
                custom_css=css)
        finally:
            os.unlink(css_path)

        self.assertIn(".program-period { fill: #00ff00; }", image)

    def test_custom_css_rejects_external_content(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".css",
                                         delete=False) as css_file:
            css_file.write(".program-period { fill: url(http://example); }")
            css_path = css_file.name
        try:
            with self.assertRaises(ValueError):
                program_visualization.load_custom_css(css_path)
        finally:
            os.unlink(css_path)
