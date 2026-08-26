import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from smarttag_detector.ble_scanner import scan_for_device


def _fake_devices(entries):
    """entries: list of (address, name, rssi) -> dict shaped like BleakScanner.discover(return_adv=True)."""
    result = {}
    for address, name, rssi in entries:
        device = MagicMock()
        device.name = name
        adv = MagicMock()
        adv.rssi = rssi
        result[address] = (device, adv)
    return result


@patch("smarttag_detector.ble_scanner.BleakScanner.discover", new_callable=AsyncMock)
def test_scan_for_device_found(mock_discover):
    mock_discover.return_value = _fake_devices([("AA:BB:CC:DD:EE:FF", "SmartTag", -45)])
    rssi = asyncio.run(scan_for_device("aa:bb:cc:dd:ee:ff"))
    assert rssi == -45


@patch("smarttag_detector.ble_scanner.BleakScanner.discover", new_callable=AsyncMock)
def test_scan_for_device_not_found(mock_discover):
    mock_discover.return_value = _fake_devices([("11:22:33:44:55:66", "Other", -50)])
    rssi = asyncio.run(scan_for_device("AA:BB:CC:DD:EE:FF"))
    assert rssi is None
