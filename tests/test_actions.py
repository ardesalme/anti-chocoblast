from unittest.mock import patch

from device_detector.actions import lock_screen


@patch("device_detector.actions.subprocess.run")
def test_lock_screen_invokes_osascript(mock_run):
    mock_run.return_value.returncode = 0
    assert lock_screen() is True
    args = mock_run.call_args[0][0]
    assert args[0] == "osascript"
    assert "control down" in args[2]
    assert "command down" in args[2]


@patch("device_detector.actions.subprocess.run")
def test_lock_screen_returns_false_on_failure(mock_run):
    import subprocess

    mock_run.side_effect = subprocess.CalledProcessError(1, "osascript")
    assert lock_screen() is False


@patch("device_detector.actions.subprocess.run")
def test_lock_screen_returns_false_when_osascript_missing(mock_run):
    mock_run.side_effect = FileNotFoundError()
    assert lock_screen() is False
