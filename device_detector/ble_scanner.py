"""BLE scanning: check whether a specific device (by identifier) is currently in range.

On macOS, CoreBluetooth never exposes a device's real hardware MAC address (Apple hides it for
privacy) - Bleak instead reports a UUID that CoreBluetooth assigns per device, per Mac. It's not
a MAC address, but it is stable, so it works fine as a matching key here.

To discover a device's identifier in the first place, use the `scan-devices` script
(device_detector/scan_devices.py) instead.
"""

from bleak import BleakScanner


async def scan_for_device(device_id: str, scan_time: float = 3.0) -> int | None:
    """Scan for a specific device identifier. Returns its RSSI if seen during the scan, else None."""
    device_id = device_id.upper()
    devices = await BleakScanner.discover(timeout=scan_time, return_adv=True)
    for address, (_device, adv) in devices.items():
        if address.upper() == device_id:
            return adv.rssi
    return None
