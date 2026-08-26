import json
from unittest.mock import MagicMock, patch

from device_detector.bt_connection import get_connection_rssi

_SAMPLE_OUTPUT = json.dumps(
    {
        "SPBluetoothDataType": [
            {
                "device_connected": [
                    {"Flip ": {"device_address": "B8:A8:25:C5:72:21", "device_rssi": "-42"}},
                ],
                "device_not_connected": [
                    {"Airdopes 141": {"device_address": "2A:48:DF:82:2C:70"}},
                ],
            }
        ]
    }
)


@patch("device_detector.bt_connection.subprocess.run")
def test_get_connection_rssi_matches_connected_device_case_insensitively(mock_run):
    mock_run.return_value = MagicMock(stdout=_SAMPLE_OUTPUT)
    assert get_connection_rssi("flip") == -42


@patch("device_detector.bt_connection.subprocess.run")
def test_get_connection_rssi_returns_none_for_disconnected_device(mock_run):
    mock_run.return_value = MagicMock(stdout=_SAMPLE_OUTPUT)
    assert get_connection_rssi("Airdopes 141") is None


@patch("device_detector.bt_connection.subprocess.run")
def test_get_connection_rssi_returns_none_for_unknown_device(mock_run):
    mock_run.return_value = MagicMock(stdout=_SAMPLE_OUTPUT)
    assert get_connection_rssi("Nonexistent") is None
