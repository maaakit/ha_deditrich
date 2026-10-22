"""Configuration helpers for persistent add-on logs."""

from __future__ import absolute_import

import logging
import os
import re
import zipfile
from logging.handlers import TimedRotatingFileHandler


def _zip_rotator(source, destination):
    temporary_destination = destination + ".tmp"
    try:
        with zipfile.ZipFile(
                temporary_destination, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.write(source, os.path.basename(source))
        os.replace(temporary_destination, destination)
        os.remove(source)
    finally:
        if os.path.exists(temporary_destination):
            os.remove(temporary_destination)


def add_persistent_file_handler(logger, log_directory, retention_days):
    """Add a daily rotating ZIP log handler to ``logger``."""
    if retention_days < 1:
        raise ValueError("Log retention must be at least one day")

    os.makedirs(log_directory, exist_ok=True)
    log_path = os.path.join(log_directory, "isystem2mqtt.log")
    handler = TimedRotatingFileHandler(
        log_path,
        when="midnight",
        interval=1,
        backupCount=retention_days,
        encoding="utf-8",
        utc=True)
    handler.namer = lambda filename: filename + ".zip"
    handler.rotator = _zip_rotator
    handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    return handler
