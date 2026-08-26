"""BLE scanning: discover nearby devices and check for a specific SmartTag by MAC address."""

import asyncio

from bleak import BleakScanner


async def discover_devices(scan_time: float = 5.0) -> list[tuple[str, str, int]]:
    """Scan for all nearby BLE devices. Returns (address, name, rssi) sorted by strongest signal first.

    Used to help the user identify their SmartTag's MAC address (bring the tag close, run the
    scan, and look for the entry with the strongest RSSI).
    """
    devices = await BleakScanner.discover(timeout=scan_time, return_adv=True)
    results = [
        (address, device.name or "Unknown", adv.rssi)
        for address, (device, adv) in devices.items()
    ]
    results.sort(key=lambda entry: entry[2], reverse=True)
    return results


async def scan_for_device(mac_address: str, scan_time: float = 3.0) -> int | None:
    """Scan for a specific MAC address. Returns its RSSI if seen during the scan, else None."""
    mac_address = mac_address.upper()
    devices = await BleakScanner.discover(timeout=scan_time, return_adv=True)
    for address, (_device, adv) in devices.items():
        if address.upper() == mac_address:
            return adv.rssi
    return None


async def _main() -> None:
    print("Scanning for nearby BLE devices (5s)...")
    devices = await discover_devices()
    if not devices:
        print("No BLE devices found. Make sure Bluetooth is enabled.")
        return
    print(f"{'MAC Address':<20} {'RSSI':>6}  Name")
    for address, name, rssi in devices:
        print(f"{address:<20} {rssi:>6}  {name}")


if __name__ == "__main__":
    asyncio.run(_main())
