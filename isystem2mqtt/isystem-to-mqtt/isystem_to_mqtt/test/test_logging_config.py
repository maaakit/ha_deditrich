"""Tests for persistent daily ZIP log rotation."""

from __future__ import absolute_import

import calendar
import datetime
import logging
import os
import tempfile
import unittest
import zipfile

from ..logging_config import add_persistent_file_handler


class TestPersistentLogging(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.logger = logging.Logger("persistent-logging-test")
        self.handler = None

    def tearDown(self):
        if self.handler is not None:
            self.logger.removeHandler(self.handler)
            self.handler.close()
        for filename in os.listdir(self.directory):
            os.remove(os.path.join(self.directory, filename))
        os.rmdir(self.directory)

    def test_daily_rotation_creates_a_zip_archive(self):
        self.handler = add_persistent_file_handler(
            self.logger, self.directory, 7)
        self.logger.info("before rotation")
        self.handler.rolloverAt = calendar.timegm(
            datetime.datetime(1970, 1, 2).timetuple())

        self.handler.doRollover()

        archive_path = os.path.join(
            self.directory, "isystem2mqtt.log.1970-01-01.zip")
        self.assertTrue(os.path.isfile(archive_path))
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(archive.namelist(), ["isystem2mqtt.log"])
            self.assertIn(
                b"before rotation",
                archive.read("isystem2mqtt.log"))
        self.assertFalse(os.path.exists(
            os.path.join(self.directory, "isystem2mqtt.log.1970-01-01")))

    def test_retention_deletes_older_zip_archives(self):
        self.handler = add_persistent_file_handler(
            self.logger, self.directory, 2)
        for day in range(1, 4):
            archive_name = "isystem2mqtt.log.2026-01-%02d.zip" % day
            with zipfile.ZipFile(
                    os.path.join(self.directory, archive_name), "w"):
                pass
        self.logger.info("new day's log")
        self.handler.rolloverAt = calendar.timegm(
            datetime.datetime(2026, 1, 5).timetuple())
        self.handler.doRollover()

        remaining = sorted(
            filename for filename in os.listdir(self.directory)
            if filename.endswith(".zip"))
        self.assertEqual(remaining, [
            "isystem2mqtt.log.2026-01-03.zip",
            "isystem2mqtt.log.2026-01-04.zip",
        ])

    def test_rejects_non_positive_retention(self):
        with self.assertRaises(ValueError):
            add_persistent_file_handler(self.logger, self.directory, 0)


if __name__ == "__main__":
    unittest.main()
