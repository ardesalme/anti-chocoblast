"""Configuration loading for SmartTag Detector."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


@dataclass
class Config:
    mac_address: str
    timeout: int
    scan_interval: int
    rssi_threshold: int
    lock_action: str
    log_level: str
    log_file: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        smarttag = data.get("smarttag", {})
        lock_behavior = data.get("lock_behavior", {})
        logging_cfg = data.get("logging", {})

        mac_address = smarttag.get("mac_address")
        if not mac_address:
            raise ValueError("config.yaml is missing smarttag.mac_address")

        return cls(
            mac_address=mac_address,
            timeout=int(smarttag.get("timeout", 30)),
            scan_interval=int(smarttag.get("scan_interval", 3)),
            rssi_threshold=int(smarttag.get("tx_power", -56)),
            lock_action=lock_behavior.get("action", "lock"),
            log_level=logging_cfg.get("level", "INFO"),
            log_file=logging_cfg.get("file", "/tmp/smarttag.log"),
        )


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> Config:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}. Copy config.example.yaml to config.yaml and set your SmartTag's MAC address."
        )
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    return Config.from_dict(data)
