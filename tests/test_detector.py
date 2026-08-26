from smarttag_detector.detector import PresenceDetector


def test_starts_unknown_then_absent_without_sighting():
    d = PresenceDetector(timeout=30)
    assert d.update(rssi=None, now=0) == "absent"
    assert not d.just_went_absent()  # unknown -> absent should not trigger a lock


def test_present_when_seen_above_threshold():
    d = PresenceDetector(timeout=30, rssi_threshold=-56)
    assert d.update(rssi=-40, now=0) == "present"
    assert d.just_went_present()


def test_weak_signal_below_threshold_does_not_count_as_seen():
    d = PresenceDetector(timeout=30, rssi_threshold=-56)
    assert d.update(rssi=-70, now=0) == "absent"


def test_goes_absent_after_timeout():
    d = PresenceDetector(timeout=30, rssi_threshold=-56)
    d.update(rssi=-40, now=0)
    assert d.update(rssi=None, now=10) == "present"  # within timeout
    assert d.update(rssi=None, now=31) == "absent"
    assert d.just_went_absent()


def test_just_went_absent_fires_once():
    d = PresenceDetector(timeout=30, rssi_threshold=-56)
    d.update(rssi=-40, now=0)
    d.update(rssi=None, now=31)
    assert d.just_went_absent()
    d.update(rssi=None, now=40)  # still absent on the next scan
    assert d.just_went_absent() is False


def test_present_again_after_returning():
    d = PresenceDetector(timeout=30, rssi_threshold=-56)
    d.update(rssi=-40, now=0)
    d.update(rssi=None, now=31)
    assert d.just_went_absent()
    d.update(rssi=-40, now=32)
    assert d.just_went_present()
