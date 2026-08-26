"""Bluetooth Classic connection status: check whether a paired device (by name) is currently
connected, via `system_profiler SPBluetoothDataType`.

This is the alternative to ble_scanner.py's address-based scan, meant for devices like phones:
once paired over classic Bluetooth, macOS reports them by a real, stable name/address and tracks
whether they're currently connected - no BLE random-address rotation to deal with. The tradeoff
is coarser granularity: "connected or not" rather than a live RSSI-based proximity reading.
"""

import json
import subprocess


def get_connection_rssi(device_name: str) -> int | None:
    """Return the paired device's RSSI if currently connected, else None (not connected/unknown)."""
    output = subprocess.run(
        ["system_profiler", "SPBluetoothDataType", "-json"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    data = json.loads(output)

    for controller in data.get("SPBluetoothDataType", []):
        for entry in controller.get("device_connected", []):
            for name, info in entry.items():
                if name.strip().lower() == device_name.strip().lower():
                    rssi = info.get("device_rssi")
                    return int(rssi) if rssi is not None else 0
    return None
