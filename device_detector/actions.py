"""Actions triggered by presence changes: locking the macOS screen."""

import logging
import subprocess

logger = logging.getLogger("smarttag_detector.actions")

_LOCK_SCRIPT = (
    'tell application "System Events" to keystroke "q" using {control down, command down}'
)


def lock_screen() -> bool:
    """Lock the macOS screen via the Control+Cmd+Q shortcut, triggered through AppleScript."""
    try:
        subprocess.run(
            ["osascript", "-e", _LOCK_SCRIPT],
            check=True,
            capture_output=True,
            timeout=10,
        )
        logger.info("Screen locked")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        logger.error("Failed to lock screen: %s", exc)
        return False
