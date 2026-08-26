"""BLE scanning: check whether a specific SmartTag (by MAC address) is currently in range.

To discover a SmartTag's MAC address in the first place, use the `scan-smarttags` script
(smarttag_detector/scan_smarttags.py) instead.
"""

from bleak import BleakScanner


async def scan_for_device(mac_address: str, scan_time: float = 3.0) -> int | None:
    """Scan for a specific MAC address. Returns its RSSI if seen during the scan, else None."""
    mac_address = mac_address.upper()
    devices = await BleakScanner.discover(timeout=scan_time, return_adv=True)
    for address, (_device, adv) in devices.items():
        if address.upper() == mac_address:
            return adv.rssi
    return None
