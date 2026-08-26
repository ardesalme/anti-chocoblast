from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from device_detector.face_scanner import is_face_present, load_reference_encoding

_REFERENCE = np.zeros(128)
_MATCHING = np.zeros(128)
_DIFFERENT = np.ones(128)


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.face_recognition.load_image_file")
def test_load_reference_encoding_returns_first_face(mock_load, mock_encodings):
    mock_encodings.return_value = [_REFERENCE, _DIFFERENT]
    assert np.array_equal(load_reference_encoding("me.jpg"), _REFERENCE)


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.face_recognition.load_image_file")
def test_load_reference_encoding_raises_when_no_face_found(mock_load, mock_encodings):
    mock_encodings.return_value = []
    with pytest.raises(ValueError, match="No face found"):
        load_reference_encoding("empty.jpg")


def _mock_camera(ok=True, frame=None):
    camera = MagicMock()
    camera.isOpened.return_value = True
    camera.read.return_value = (ok, frame if frame is not None else np.zeros((10, 10, 3)))
    return camera


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_true_when_encoding_matches(mock_video_capture, mock_encodings):
    mock_video_capture.return_value = _mock_camera()
    mock_encodings.return_value = [_MATCHING]
    assert is_face_present(_REFERENCE, tolerance=0.6) is True


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_false_when_no_face_in_frame(mock_video_capture, mock_encodings):
    mock_video_capture.return_value = _mock_camera()
    mock_encodings.return_value = []
    assert is_face_present(_REFERENCE, tolerance=0.6) is False


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_false_when_frame_grab_fails(mock_video_capture, mock_encodings):
    mock_video_capture.return_value = _mock_camera(ok=False)
    assert is_face_present(_REFERENCE, tolerance=0.6) is False
    mock_encodings.assert_not_called()


@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_raises_when_camera_unavailable(mock_video_capture):
    camera = MagicMock()
    camera.isOpened.return_value = False
    mock_video_capture.return_value = camera
    with pytest.raises(RuntimeError, match="Could not open camera"):
        is_face_present(_REFERENCE)
