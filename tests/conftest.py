"""Stub out the `bleak` package for tests running where it isn't installed (e.g. non-macOS CI).

BLE behavior itself is never exercised by the test suite - tests patch
`smarttag_detector.ble_scanner.BleakScanner.discover` directly - so a minimal stub is enough to
satisfy the `from bleak import BleakScanner` import.
"""

import sys
import types

if "bleak" not in sys.modules:
    fake_bleak = types.ModuleType("bleak")

    class _StubBleakScanner:
        @staticmethod
        async def discover(*args, **kwargs):
            return {}

    fake_bleak.BleakScanner = _StubBleakScanner
    sys.modules["bleak"] = fake_bleak
