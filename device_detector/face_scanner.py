"""Presence via webcam face recognition: check whether a known face is currently visible.

Requires a reference photo (a clear, front-facing shot) to compute the face encoding matched
against each check. Captures a single frame per check - no continuous video stream - to keep
camera usage minimal.
"""

import cv2
import face_recognition
import numpy as np


def load_reference_encoding(image_path: str) -> np.ndarray:
    """Compute the face encoding to match against, from a reference photo."""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        raise ValueError(f"No face found in reference image: {image_path}")
    return encodings[0]


def is_face_present(reference_encoding: np.ndarray, camera_index: int = 0, tolerance: float = 0.6) -> bool:
    """Grab one webcam frame and check whether the reference face appears in it."""
    camera = cv2.VideoCapture(camera_index)
    try:
        if not camera.isOpened():
            raise RuntimeError(f"Could not open camera at index {camera_index}")
        ok, frame = camera.read()
    finally:
        camera.release()

    if not ok:
        return False

    rgb_frame = frame[:, :, ::-1]
    encodings = face_recognition.face_encodings(rgb_frame)
    return any(
        face_recognition.face_distance([reference_encoding], encoding)[0] <= tolerance
        for encoding in encodings
    )
