"""Entry point: continuously scans for the configured device and locks the screen when it's gone."""

import argparse
import asyncio
from collections.abc import Awaitable, Callable

from .actions import lock_screen
from .ble_scanner import scan_for_device
from .bt_connection import get_connection_rssi
from .config import Config, load_config
from .detector import PresenceDetector
from .face_scanner import is_face_present, load_reference_encoding
from .logger import get_logger


async def _make_checker(config: Config) -> Callable[[], Awaitable[int | None]]:
    """Build the async () -> RSSI-or-None presence check for the configured method.

    Each check also accounts for `scan_interval`: the BLE scan blocks for that long by design,
    while the other methods explicitly sleep, so the loop always paces itself the same way.
    """
    if config.method == "ble":

        async def check() -> int | None:
            return await scan_for_device(config.device_id, scan_time=config.scan_interval)

        return check

    if config.method == "bluetooth":

        async def check() -> int | None:
            rssi = await asyncio.to_thread(get_connection_rssi, config.device_name)
            await asyncio.sleep(config.scan_interval)
            return rssi

        return check

    reference_encoding = await asyncio.to_thread(load_reference_encoding, config.face_image)

    async def check() -> int | None:
        present = await asyncio.to_thread(
            is_face_present, reference_encoding, config.camera_index, config.face_tolerance
        )
        await asyncio.sleep(config.scan_interval)
        return 0 if present else None

    return check


def _label(config: Config) -> str:
    return {"bluetooth": config.device_name, "face": config.face_image}.get(config.method, config.device_id)


async def run(config_path: str, once: bool) -> None:
    config = load_config(config_path)
    logger = get_logger("device_detector", level=config.log_level, log_file=config.log_file)
    detector = PresenceDetector(timeout=config.timeout, rssi_threshold=config.rssi_threshold)
    check_presence = await _make_checker(config)
    label = _label(config)

    logger.info(
        "Watching for %s via %s (timeout=%ss, scan_interval=%ss)",
        label,
        config.method,
        config.timeout,
        config.scan_interval,
    )

    while True:
        rssi = await check_presence()
        state = detector.update(rssi)

        if rssi is not None:
            logger.debug("Saw %s at RSSI %s -> %s", label, rssi, state)
        else:
            logger.debug("Did not see %s -> %s", label, state)

        if detector.just_went_present():
            logger.info("Device detected, Mac is unlocked/present")
        elif detector.just_went_absent():
            logger.info("Device absent for over %ss, locking screen", config.timeout)
            lock_screen()

        if once:
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Device Detector - Phase 1 MVP")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument(
        "--once", action="store_true", help="Run a single scan cycle and exit (manual testing)"
    )
    args = parser.parse_args()
    asyncio.run(run(args.config, args.once))


if __name__ == "__main__":
    main()
