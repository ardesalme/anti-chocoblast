"""Standalone script: repeatedly scan for nearby BLE devices to find your device's identifier.

Samsung's Bluetooth SIG company ID (0x0075) is used to flag likely SmartTags in the results, as
a hint - not a guarantee, since advertisement contents vary. Bring the device close to the Mac
and look for the entry with the strongest (least negative) RSSI.

Note: on macOS, CoreBluetooth never exposes a device's real hardware MAC address (Apple hides it
for privacy) - the "address" shown below is actually a UUID that CoreBluetooth assigns per
device, per Mac. It's not a MAC address, but it's stable, so it works fine as the identifier to
put in config.yaml.
"""

import argparse
import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime

from bleak import BleakScanner

SAMSUNG_COMPANY_ID = 0x0075

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"


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


def _use_color() -> bool:
    return sys.stdout.isatty()


def _style(text: str, *codes: str) -> str:
    if not _use_color():
        return text
    return "".join(codes) + text + _RESET


def _rssi_color(rssi: int) -> str:
    if rssi >= -50:
        return _GREEN
    if rssi >= -70:
        return _YELLOW
    return _RED


def _signal_bar(rssi: int, width: int = 10) -> str:
    """Rough visual proximity gauge: -30 dBm (very close) .. -100 dBm (far) mapped to a bar."""
    strength = max(0.0, min(1.0, (rssi + 100) / 70))
    filled = round(strength * width)
    return "█" * filled + "░" * (width - filled)


def print_table(devices: list[BleDevice], samsung_only: bool) -> None:
    rows = [d for d in devices if d.is_samsung] if samsung_only else devices
    if not rows:
        msg = "No Samsung devices found." if samsung_only else "No BLE devices found."
        print(_style(msg, _DIM))
        return

    header = f"  {'Identifier':<36} {'RSSI':>6}  {'Signal':<10} {'Tag':<7} Name"
    print(_style(header, _BOLD))
    print(_style("-" * len(header), _DIM))

    closest_samsung_marked = False
    for d in rows:
        color = _rssi_color(d.rssi)
        marker = " "
        if d.is_samsung and not closest_samsung_marked:
            marker = _style("➔", _BOLD, _GREEN)
            closest_samsung_marked = True

        addr_col = f"{d.address:<36}"
        rssi_col = _style(f"{d.rssi:>6}", color)
        bar_col = _style(_signal_bar(d.rssi), color)
        tag_col = _style(f"{'SAMSUNG':<7}", _BOLD, _CYAN) if d.is_samsung else " " * 7

        print(f"{marker} {addr_col} {rssi_col}  {bar_col} {tag_col} {d.name}")


def _clear_screen() -> None:
    if _use_color():
        print("\033[H\033[2J", end="")


async def run(scan_time: float, cycles: int | None, samsung_only: bool) -> None:
    print(_style("Bring your device close to this Mac for the strongest signal.", _BOLD))
    print(f"Scanning every {scan_time:.0f}s. Press Ctrl+C to stop.\n")
    count = 0
    while cycles is None or count < cycles:
        devices = await scan_once(scan_time)
        count += 1
        _clear_screen()
        cycle_label = f"cycle {count}/{cycles}" if cycles else f"cycle {count}"
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(_style(f"Device scan — {timestamp} ({cycle_label})", _BOLD, _CYAN))
        print()
        print_table(devices, samsung_only)
        print()
    print("Copy the identifier of your device into config.yaml (device.device_id).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan for nearby BLE devices to find your device's identifier."
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
