from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from device_detector.face_scanner import is_face_present, load_reference_encodings

_REFERENCE_A = np.zeros(128)
_REFERENCE_B = np.full(128, 5.0)
_MATCHING_A = np.zeros(128)
_STRANGER = np.full(128, 5.0) - 10  # far from both references


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.face_recognition.load_image_file")
def test_load_reference_encodings_returns_first_face_per_image(mock_load, mock_encodings):
    mock_encodings.side_effect = [[_REFERENCE_A], [_REFERENCE_B]]
    encodings = load_reference_encodings(["me.jpg", "me2.jpg"])
    assert np.array_equal(encodings[0], _REFERENCE_A)
    assert np.array_equal(encodings[1], _REFERENCE_B)


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.face_recognition.load_image_file")
def test_load_reference_encodings_raises_when_no_face_found(mock_load, mock_encodings):
    mock_encodings.return_value = []
    with pytest.raises(ValueError, match="No face found"):
        load_reference_encodings(["empty.jpg"])


def test_load_reference_encodings_raises_when_no_images_found():
    with pytest.raises(ValueError, match="No reference images found"):
        load_reference_encodings([])


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.face_recognition.load_image_file")
def test_load_reference_encodings_expands_a_directory(mock_load, mock_encodings, tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"")
    (tmp_path / "b.png").write_bytes(b"")
    (tmp_path / "notes.txt").write_bytes(b"")  # non-image file, should be skipped
    mock_encodings.return_value = [_REFERENCE_A]

    load_reference_encodings([str(tmp_path)])

    loaded_paths = sorted(call.args[0] for call in mock_load.call_args_list)
    assert loaded_paths == sorted([str(tmp_path / "a.jpg"), str(tmp_path / "b.png")])


def _mock_camera(ok=True, frame=None):
    camera = MagicMock()
    camera.isOpened.return_value = True
    camera.read.return_value = (ok, frame if frame is not None else np.zeros((10, 10, 3), dtype=np.uint8))
    return camera


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_true_when_any_reference_matches(mock_video_capture, mock_encodings):
    mock_video_capture.return_value = _mock_camera()
    mock_encodings.return_value = [_MATCHING_A]
    assert is_face_present([_REFERENCE_A, _REFERENCE_B], tolerance=0.6) is True


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_true_when_known_face_alongside_a_stranger(mock_video_capture, mock_encodings):
    mock_video_capture.return_value = _mock_camera()
    mock_encodings.return_value = [_STRANGER, _MATCHING_A]
    assert is_face_present([_REFERENCE_A], tolerance=0.6) is True


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_false_when_only_a_stranger_in_frame(mock_video_capture, mock_encodings):
    mock_video_capture.return_value = _mock_camera()
    mock_encodings.return_value = [_STRANGER]
    assert is_face_present([_REFERENCE_A, _REFERENCE_B], tolerance=0.6) is False


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_false_when_no_face_in_frame(mock_video_capture, mock_encodings):
    mock_video_capture.return_value = _mock_camera()
    mock_encodings.return_value = []
    assert is_face_present([_REFERENCE_A], tolerance=0.6) is False


@patch("device_detector.face_scanner.face_recognition.face_encodings")
@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_false_when_frame_grab_fails(mock_video_capture, mock_encodings):
    mock_video_capture.return_value = _mock_camera(ok=False)
    assert is_face_present([_REFERENCE_A], tolerance=0.6) is False
    mock_encodings.assert_not_called()


@patch("device_detector.face_scanner.cv2.VideoCapture")
def test_is_face_present_raises_when_camera_unavailable(mock_video_capture):
    camera = MagicMock()
    camera.isOpened.return_value = False
    mock_video_capture.return_value = camera
    with pytest.raises(RuntimeError, match="Could not open camera"):
        is_face_present([_REFERENCE_A])
