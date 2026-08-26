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
poetry run python -m smarttag_detector.ble_scanner
```

This lists nearby BLE devices sorted by signal strength. The SmartTag should be
one of the strongest signals. Copy its MAC address into `config.yaml`.

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
  main.py         # entry point / detection loop
  ble_scanner.py  # BLE discovery + targeted scan for the configured MAC
  detector.py     # presence state machine (timeout-based)
  actions.py      # screen lock via AppleScript
  config.py       # config.yaml loading
  logger.py       # logging setup
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
