"""Standalone script: repeatedly scan for nearby BLE devices to find your SmartTag's MAC address.

Samsung's Bluetooth SIG company ID (0x0075) is used to flag likely SmartTags in the results, as
a hint - not a guarantee, since advertisement contents vary. Bring the tag close to the Mac and
look for the entry with the strongest (least negative) RSSI.
"""

import argparse
import asyncio
from dataclasses import dataclass

from bleak import BleakScanner

SAMSUNG_COMPANY_ID = 0x0075


@dataclass
class BleDevice:
    address: str
    name: str
    rssi: int
    is_samsung: bool


async def scan_once(scan_time: float) -> list[BleDevice]:
    """Run a single scan window. Returns devices sorted by strongest signal first."""
    devices = await BleakScanner.discover(timeout=scan_time, return_adv=True)
    results = [
        BleDevice(
            address=address,
            name=device.name or "Unknown",
            rssi=adv.rssi,
            is_samsung=SAMSUNG_COMPANY_ID in adv.manufacturer_data,
        )
        for address, (device, adv) in devices.items()
    ]
    results.sort(key=lambda d: d.rssi, reverse=True)
    return results


def print_table(devices: list[BleDevice], samsung_only: bool) -> None:
    rows = [d for d in devices if d.is_samsung] if samsung_only else devices
    if not rows:
        print("No Samsung devices found." if samsung_only else "No BLE devices found.")
        return
    print(f"{'MAC Address':<20} {'RSSI':>6}  {'Samsung?':<8} Name")
    for d in rows:
        print(f"{d.address:<20} {d.rssi:>6}  {'yes' if d.is_samsung else '':<8} {d.name}")


async def run(scan_time: float, cycles: int | None, samsung_only: bool) -> None:
    print("Bring your SmartTag close to this Mac for the strongest signal.")
    print(f"Scanning every {scan_time:.0f}s. Press Ctrl+C to stop.\n")
    count = 0
    while cycles is None or count < cycles:
        devices = await scan_once(scan_time)
        print_table(devices, samsung_only)
        print()
        count += 1
    print("Copy the MAC address of your SmartTag into config.yaml (smarttag.mac_address).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan for nearby BLE devices to find your SmartTag's MAC address."
    )
    parser.add_argument("--scan-time", type=float, default=5.0, help="Seconds per scan cycle")
    parser.add_argument(
        "--cycles", type=int, default=None, help="Number of scan cycles (default: run until Ctrl+C)"
    )
    parser.add_argument(
        "--samsung-only",
        action="store_true",
        help="Only show devices broadcasting Samsung manufacturer data",
    )
    args = parser.parse_args()
    try:
        asyncio.run(run(args.scan_time, args.cycles, args.samsung_only))
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
