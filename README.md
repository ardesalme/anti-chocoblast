# SmartTag Detector — Phase 1 MVP

Detects the proximity of a Samsung SmartTag over Bluetooth LE and locks the Mac's
screen when the tag has been out of range for too long.

Requires macOS (10.13+), Python 3.11.6, and a real Bluetooth adapter — BLE
scanning and the screen lock action cannot be exercised on non-macOS systems.

## Setup

Dependencies are managed with [Poetry](https://python-poetry.org/):

```bash
poetry install
```

## 1. Find your SmartTag's MAC address

Bring the SmartTag close to your Mac, then run:

```bash
poetry run scan-smarttags
```

This scans repeatedly and lists nearby BLE devices sorted by signal strength,
flagging devices that broadcast Samsung's manufacturer ID as likely SmartTags.
Press Ctrl+C to stop once you've spotted it, then copy its MAC address into
`config.yaml`. Useful flags:

```bash
poetry run scan-smarttags --samsung-only   # only show flagged Samsung devices
poetry run scan-smarttags --cycles 3       # stop after 3 scan cycles instead of running forever
poetry run scan-smarttags --scan-time 10   # widen each scan window (seconds)
```

## 2. Configure

Edit `config.yaml`:

```yaml
smarttag:
  mac_address: "AA:BB:CC:DD:EE:FF"
  timeout: 30       # seconds of absence before locking
  scan_interval: 3  # seconds per scan
  tx_power: -56     # minimum RSSI to count as "present"
```

## 3. Run

```bash
# Continuous detection loop
poetry run python -m smarttag_detector.main --config config.yaml

# Single scan cycle, for manual testing
poetry run python -m smarttag_detector.main --config config.yaml --once

# Or, via the installed script entry point
poetry run smarttag-detector --config config.yaml
```

## Tests

```bash
poetry run pytest
```

## Project layout

```
smarttag_detector/
  main.py             # entry point / detection loop
  ble_scanner.py      # targeted scan for the configured MAC (used by main.py)
  scan_smarttags.py   # standalone script to discover nearby SmartTags and their MAC address
  detector.py         # presence state machine (timeout-based)
  actions.py          # screen lock via AppleScript
  config.py           # config.yaml loading
  logger.py           # logging setup
tests/            # unit tests (pure-logic + mocked BLE/subprocess, run on any OS)
config.yaml
pyproject.toml
```

## Phase 1 success criteria

- Detects the SmartTag in under 5 seconds
- Locks the screen after 30s of absence
- Recognizes presence immediately on return
- No crashes over 1h of testing

Later phases (not part of this MVP): BLE reconnection/error handling, `.env`
config, LaunchAgent auto-start, install/uninstall scripts, and a monitoring
dashboard.
