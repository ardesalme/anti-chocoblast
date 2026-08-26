"""Configuration loading for Device Detector."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

VALID_METHODS = ("ble", "bluetooth", "face")


@dataclass
class Config:
    method: str
    device_id: str | None
    device_name: str | None
    face_image: str | None
    camera_index: int
    face_tolerance: float
    timeout: int
    scan_interval: int
    rssi_threshold: int | None
    lock_action: str
    log_level: str
    log_file: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        device_cfg = data.get("device", {})
        lock_behavior = data.get("lock_behavior", {})
        logging_cfg = data.get("logging", {})

        method = device_cfg.get("method", "ble")
        if method not in VALID_METHODS:
            raise ValueError(f"config.yaml: device.method must be one of {VALID_METHODS}, got {method!r}")

        device_id = device_cfg.get("device_id")
        device_name = device_cfg.get("device_name")
        face_image = device_cfg.get("face_image")
        rssi_threshold = device_cfg.get("tx_power")

        if method == "ble":
            if not device_id:
                raise ValueError("config.yaml is missing device.device_id (required for method: ble)")
            rssi_threshold = int(rssi_threshold) if rssi_threshold is not None else -56
        elif method == "bluetooth":
            if not device_name:
                raise ValueError("config.yaml is missing device.device_name (required for method: bluetooth)")
            rssi_threshold = None
        else:
            if not face_image:
                raise ValueError("config.yaml is missing device.face_image (required for method: face)")
            rssi_threshold = None

        return cls(
            method=method,
            device_id=device_id,
            device_name=device_name,
            face_image=face_image,
            camera_index=int(device_cfg.get("camera_index", 0)),
            face_tolerance=float(device_cfg.get("face_tolerance", 0.6)),
            timeout=int(device_cfg.get("timeout", 30)),
            scan_interval=int(device_cfg.get("scan_interval", 3)),
            rssi_threshold=rssi_threshold,
            lock_action=lock_behavior.get("action", "lock"),
            log_level=logging_cfg.get("level", "INFO"),
            log_file=logging_cfg.get("file", "/tmp/device_detector.log"),
        )


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> Config:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}. Copy config.example.yaml to config.yaml and set your device's Bluetooth identifier."
        )
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    return Config.from_dict(data)
