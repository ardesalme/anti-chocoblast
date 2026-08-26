import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from device_detector.scan_devices import SAMSUNG_COMPANY_ID, print_table, scan_once


def _fake_devices(entries):
    """entries: list of (address, name, rssi, manufacturer_ids)."""
    result = {}
    for address, name, rssi, manufacturer_ids in entries:
        device = MagicMock()
        device.name = name
        adv = MagicMock()
        adv.rssi = rssi
        adv.manufacturer_data = {mid: b"" for mid in manufacturer_ids}
        result[address] = (device, adv)
    return result


@patch("device_detector.scan_devices.BleakScanner.discover", new_callable=AsyncMock)
def test_scan_once_flags_samsung_devices_and_sorts_by_rssi(mock_discover):
    mock_discover.return_value = _fake_devices(
        [
            ("AA:AA:AA:AA:AA:AA", "Other", -70, [0x004C]),
            ("BB:BB:BB:BB:BB:BB", "Device2", -40, [SAMSUNG_COMPANY_ID]),
        ]
    )
    devices = asyncio.run(scan_once(scan_time=1.0))
    assert devices[0].address == "BB:BB:BB:BB:BB:BB"
    assert devices[0].is_samsung is True
    assert devices[1].is_samsung is False


def test_print_table_samsung_only_filters_out_non_samsung(capsys):
    from device_detector.scan_devices import BleDevice

    devices = [
        BleDevice(address="AA:AA:AA:AA:AA:AA", name="Other", rssi=-70, is_samsung=False),
        BleDevice(address="BB:BB:BB:BB:BB:BB", name="Device2", rssi=-40, is_samsung=True),
    ]
    print_table(devices, samsung_only=True)
    out = capsys.readouterr().out
    assert "BB:BB:BB:BB:BB:BB" in out
    assert "AA:AA:AA:AA:AA:AA" not in out


def test_print_table_no_devices_found(capsys):
    print_table([], samsung_only=False)
    assert "No BLE devices found." in capsys.readouterr().out
