"""Presence logic: tracks whether the SmartTag has been seen recently and flags absence timeouts."""

import time


class PresenceDetector:
    """Tracks SmartTag presence based on RSSI sightings and a timeout.

    Call `update(rssi)` after each scan with the RSSI seen (or None if not seen). It returns the
    current state ("present" or "absent"). Use `just_went_absent()` / `just_went_present()` right
    after `update()` to trigger an action exactly once on the transition.
    """

    def __init__(self, timeout: int, rssi_threshold: int | None = None):
        self.timeout = timeout
        self.rssi_threshold = rssi_threshold
        self.last_seen: float | None = None
        self.state = "unknown"
        self._previous_state = "unknown"

    def update(self, rssi: int | None, now: float | None = None) -> str:
        now = now if now is not None else time.monotonic()
        self._previous_state = self.state

        seen = rssi is not None and (self.rssi_threshold is None or rssi >= self.rssi_threshold)
        if seen:
            self.last_seen = now

        if self.last_seen is None:
            self.state = "absent"
        elif now - self.last_seen > self.timeout:
            self.state = "absent"
        else:
            self.state = "present"

        return self.state

    def just_went_absent(self) -> bool:
        # Only fires on a present -> absent transition, not on first sighting ("unknown" -> absent),
        # so the Mac isn't locked before the SmartTag has ever been detected.
        return self._previous_state == "present" and self.state == "absent"

    def just_went_present(self) -> bool:
        return self._previous_state != "present" and self.state == "present"
