# Device Detector — Phase 1 MVP

Detects the proximity of a BLE device (e.g. a Samsung SmartTag, or your phone
once paired) and locks the Mac's screen when the device has been out of range
for too long.

Requires macOS (10.13+), Python 3.11.6, and a real Bluetooth adapter — BLE
scanning and the screen lock action cannot be exercised on non-macOS systems.
The `face` method additionally requires a webcam and grants Camera access
(System Settings > Privacy & Security > Camera) to whatever runs the process.

## Setup

Dependencies are managed with [Poetry](https://python-poetry.org/):

```bash
poetry install
```

## 1. Find your device's identifier

Bring the device close to your Mac, then run:

```bash
poetry run scan-devices
```

This scans repeatedly and lists nearby BLE devices sorted by signal strength,
flagging devices that broadcast Samsung's manufacturer ID as likely SmartTags.
Press Ctrl+C to stop once you've spotted it, then copy its identifier into
`config.yaml`.

> **Note:** macOS never exposes a device's real Bluetooth MAC address to apps
> (CoreBluetooth hides it for privacy). What you'll see instead is a UUID like
> `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX` — that's expected, not a bug. It's
> assigned per device, per Mac, and stays stable, so it works fine here. If
> you're using your phone instead of a dedicated tag, pair it with the Mac
> first (System Settings > Bluetooth) — otherwise its BLE address rotates
> randomly and won't stay matchable.

Useful flags:

```bash
poetry run scan-devices --samsung-only   # only show flagged Samsung devices
poetry run scan-devices --cycles 3       # stop after 3 scan cycles instead of running forever
poetry run scan-devices --scan-time 10   # widen each scan window (seconds)
```

## 2. Configure

Edit `config.yaml`. Three detection methods are supported:

```yaml
# method: "ble" - address scan, for a dedicated tag (SmartTag, AirTag, ...)
device:
  method: "ble"
  device_id: "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
  timeout: 30       # seconds of absence before locking
  scan_interval: 3  # seconds per scan
  tx_power: -56     # minimum RSSI to count as "present"
```

```yaml
# method: "bluetooth" - classic pairing connection status, for a phone
device:
  method: "bluetooth"
  device_name: "phone name"  # the paired device's Bluetooth name (see: system_profiler SPBluetoothDataType)
  timeout: 30
  scan_interval: 3
```

BLE tags advertise continuously and don't need pairing, but phones randomize
their BLE address unless paired, which breaks address-based matching - hence
the `bluetooth` method, which instead checks whether the paired device is
currently connected over classic Bluetooth.

```yaml
# method: "face" - webcam face recognition, no paired device needed at all
device:
  method: "face"
  face_images: ["me.jpg", "me2.jpg"]  # one or more clear, front-facing reference photos
  camera_index: 0                     # which webcam to use (0 = default/built-in)
  face_tolerance: 0.6                 # lower = stricter match (0.4-0.6 typical)
  timeout: 30
  scan_interval: 3
```

`face` checks each `scan_interval` whether any reference face is visible to
the webcam - useful if you'd rather not rely on any paired accessory at all,
at the cost of needing a clear line of sight to the camera and being more
sensitive to lighting/angle than a Bluetooth-based method. Presence only
requires *one* of your reference photos to match *one* of the faces seen -
other people in frame don't prevent a match, and multiple reference photos
(different angles/lighting) make matching more forgiving.

## 3. Run

```bash
# Continuous detection loop
poetry run python -m device_detector.main --config config.yaml

# Single scan cycle, for manual testing
poetry run python -m device_detector.main --config config.yaml --once

# Or, via the installed script entry point
poetry run device-detector --config config.yaml
```

## Tests

```bash
poetry run pytest
```

## Project layout

```
device_detector/
  main.py             # entry point / detection loop
  ble_scanner.py      # method: ble - targeted BLE address scan (used by main.py)
  bt_connection.py    # method: bluetooth - paired device connection status (used by main.py)
  face_scanner.py     # method: face - webcam face recognition (used by main.py)
  scan_devices.py     # standalone script to discover nearby devices and their identifier
  detector.py         # presence state machine (timeout-based)
  actions.py          # screen lock via AppleScript
  config.py           # config.yaml loading
  logger.py           # logging setup
tests/            # unit tests (pure-logic + mocked BLE/subprocess, run on any OS)
config.yaml
pyproject.toml
```

## Phase 1 success criteria

- Detects the device in under 5 seconds
- Locks the screen after 30s of absence
- Recognizes presence immediately on return
- No crashes over 1h of testing

Later phases (not part of this MVP): BLE reconnection/error handling,
LaunchAgent auto-start, install/uninstall scripts, and a monitoring
dashboard.
