"""Entry point: continuously scans for the configured SmartTag and locks the screen when it's gone."""

import argparse
import asyncio

from .actions import lock_screen
from .ble_scanner import scan_for_device
from .config import load_config
from .detector import PresenceDetector
from .logger import get_logger


async def run(config_path: str, once: bool) -> None:
    config = load_config(config_path)
    logger = get_logger("smarttag_detector", level=config.log_level, log_file=config.log_file)
    detector = PresenceDetector(timeout=config.timeout, rssi_threshold=config.rssi_threshold)

    logger.info(
        "Watching for %s (timeout=%ss, scan_interval=%ss)",
        config.mac_address,
        config.timeout,
        config.scan_interval,
    )

    while True:
        rssi = await scan_for_device(config.mac_address, scan_time=config.scan_interval)
        state = detector.update(rssi)

        if rssi is not None:
            logger.debug("Saw %s at RSSI %s -> %s", config.mac_address, rssi, state)
        else:
            logger.debug("Did not see %s -> %s", config.mac_address, state)

        if detector.just_went_present():
            logger.info("SmartTag detected, Mac is unlocked/present")
        elif detector.just_went_absent():
            logger.info("SmartTag absent for over %ss, locking screen", config.timeout)
            lock_screen()

        if once:
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="SmartTag Detector - Phase 1 MVP")
    parser.add_argument("--config", default="config.yaml", help="Path to config.yaml")
    parser.add_argument(
        "--once", action="store_true", help="Run a single scan cycle and exit (manual testing)"
    )
    args = parser.parse_args()
    asyncio.run(run(args.config, args.once))


if __name__ == "__main__":
    main()
