import pytest

from device_detector.config import Config

_BASE = {"device": {"method": "bluetooth", "device_name": "Flip"}}


def test_from_dict_uses_yaml_defaults():
    config = Config.from_dict(_BASE)
    assert config.timeout == 30
    assert config.scan_interval == 3


def test_from_dict_uses_yaml_overrides():
    config = Config.from_dict({"device": {**_BASE["device"], "timeout": 15, "scan_interval": 2}})
    assert config.timeout == 15
    assert config.scan_interval == 2


def test_from_dict_requires_device_id_for_ble_method():
    with pytest.raises(ValueError, match="device_id"):
        Config.from_dict({"device": {"method": "ble"}})


def test_from_dict_requires_device_name_for_bluetooth_method():
    with pytest.raises(ValueError, match="device_name"):
        Config.from_dict({"device": {"method": "bluetooth"}})


def test_from_dict_requires_face_image_for_face_method():
    with pytest.raises(ValueError, match="face_image"):
        Config.from_dict({"device": {"method": "face"}})


def test_from_dict_uses_face_defaults():
    config = Config.from_dict({"device": {"method": "face", "face_image": "me.jpg"}})
    assert config.camera_index == 0
    assert config.face_tolerance == 0.6
    assert config.rssi_threshold is None


def test_from_dict_rejects_unknown_method():
    with pytest.raises(ValueError, match="method"):
        Config.from_dict({"device": {"method": "carrier-pigeon"}})
