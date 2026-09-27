"""Unit tests for resilient Modbus writes."""

try:
    import unittest.mock as mock
except ImportError:
    import mock

import unittest

import minimalmodbus

from .. import modbus_write


class TestWriteWithRetries(unittest.TestCase):
    def setUp(self):
        self.instrument = mock.Mock()
        sleep_patch = mock.patch("isystem_to_mqtt.modbus_write.time.sleep")
        self.addCleanup(sleep_patch.stop)
        self.sleep = sleep_patch.start()

    def test_retries_no_response_then_succeeds(self):
        write_operation = mock.Mock(side_effect=[
            minimalmodbus.NoResponseError("no response"),
            None,
        ])

        result = modbus_write.write_with_retries(
            self.instrument, write_operation, "test write")

        self.assertTrue(result)
        self.assertEqual(write_operation.call_count, 2)
        self.instrument.wait_time_slot.assert_called_once_with()
        self.sleep.assert_called_once_with(modbus_write.WRITE_RETRY_DELAY)

    def test_stops_after_two_retries_and_continues(self):
        write_operation = mock.Mock(
            side_effect=minimalmodbus.NoResponseError("no response"))

        with self.assertLogs("isystem_to_mqtt.modbus_write", level="ERROR"):
            result = modbus_write.write_with_retries(
                self.instrument, write_operation, "test write")

        self.assertFalse(result)
        self.assertEqual(
            write_operation.call_count, modbus_write.WRITE_RETRY_COUNT + 1)
        self.assertEqual(
            self.instrument.wait_time_slot.call_count,
            modbus_write.WRITE_RETRY_COUNT)
        self.assertEqual(
            self.sleep.call_count, modbus_write.WRITE_RETRY_COUNT)

    def test_does_not_retry_non_transient_error(self):
        write_operation = mock.Mock(side_effect=ValueError("invalid value"))

        with self.assertLogs("isystem_to_mqtt.modbus_write", level="ERROR"):
            result = modbus_write.write_with_retries(
                self.instrument, write_operation, "test write")

        self.assertFalse(result)
        write_operation.assert_called_once_with()
        self.instrument.wait_time_slot.assert_not_called()
        self.sleep.assert_not_called()
