"""Presence via webcam face recognition: check whether a known face is currently visible.

Requires one or more reference photos (clear, front-facing shots) to compute the face encodings
matched against each check. Multiple photos improve tolerance to lighting/angle by giving the
matcher several looks at the same face instead of just one. Captures a single frame per check -
no continuous video stream - to keep camera usage minimal.

Presence only requires the known face to be one of the faces seen - other people in frame don't
prevent a match.
"""

from pathlib import Path

import cv2
import face_recognition
import numpy as np

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def _resolve_image_paths(paths: list[str]) -> list[str]:
    """Expand any directory in `paths` to the image files it directly contains."""
    resolved = []
    for path in paths:
        p = Path(path)
        if p.is_dir():
            resolved.extend(sorted(str(f) for f in p.iterdir() if f.suffix.lower() in _IMAGE_EXTENSIONS))
        else:
            resolved.append(str(p))
    return resolved


def load_reference_encodings(image_paths: list[str]) -> list[np.ndarray]:
    """Compute the face encodings to match against, one per reference photo.

    Entries in `image_paths` may be individual image files or directories - directories are
    expanded to every image file they directly contain.
    """
    resolved_paths = _resolve_image_paths(image_paths)
    if not resolved_paths:
        raise ValueError(f"No reference images found in: {image_paths}")

    encodings = []
    for image_path in resolved_paths:
        image = face_recognition.load_image_file(image_path)
        found = face_recognition.face_encodings(image)
        if not found:
            raise ValueError(f"No face found in reference image: {image_path}")
        encodings.append(found[0])
    return encodings


def is_face_present(reference_encodings: list[np.ndarray], camera_index: int = 0, tolerance: float = 0.6) -> bool:
    """Grab one webcam frame and check whether any reference face appears in it."""
    camera = cv2.VideoCapture(camera_index)
    try:
        if not camera.isOpened():
            raise RuntimeError(f"Could not open camera at index {camera_index}")
        ok, frame = camera.read()
    finally:
        camera.release()

    if not ok:
        return False

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    seen_encodings = face_recognition.face_encodings(rgb_frame)
    return any(
        (face_recognition.face_distance(reference_encodings, seen) <= tolerance).any()
        for seen in seen_encodings
    )
