"""Helpers for resilient Modbus writes."""

import logging
import time

import minimalmodbus


_LOGGER = logging.getLogger(__name__)
WRITE_RETRY_COUNT = 2
WRITE_RETRY_DELAY = 1


def write_with_retries(instrument, write_operation, description):
    """Retry transient Modbus write failures without stopping the polling loop."""
    for attempt in range(WRITE_RETRY_COUNT + 1):
        try:
            if attempt:
                time.sleep(WRITE_RETRY_DELAY)
                instrument.wait_time_slot()
            write_operation()
            return True
        except (minimalmodbus.NoResponseError, EnvironmentError):
            if attempt < WRITE_RETRY_COUNT:
                _LOGGER.warning(
                    "%s failed, retrying in %ds (attempt %d/%d)...",
                    description, WRITE_RETRY_DELAY, attempt + 1,
                    WRITE_RETRY_COUNT, exc_info=True)
                continue
            _LOGGER.error(
                "%s failed after %d attempts; continuing.",
                description, WRITE_RETRY_COUNT + 1, exc_info=True)
        except (minimalmodbus.ModbusException, UnicodeDecodeError, ValueError):
            _LOGGER.error("%s failed; continuing.", description, exc_info=True)
        return False

    return False
