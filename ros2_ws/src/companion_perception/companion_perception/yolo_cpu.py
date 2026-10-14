"""Optional CPU YOLO inference (Ultralytics) when a model file is present."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisionDetection:
    """One detection result from YOLO CPU inference."""

    label: str
    confidence: float


def try_load_yolo(model_path: str):
    """Load an Ultralytics model or return None when unavailable."""
    if not model_path:
        return None
    try:
        from ultralytics import YOLO
    except ImportError:
        return None
    try:
        return YOLO(model_path)
    except Exception:
        return None


def detect_in_frame(model, frame) -> list[VisionDetection]:
    """Run YOLO on a BGR uint8 numpy frame."""
    if model is None or frame is None:
        return []
    try:
        results = model.predict(frame, verbose=False)
    except Exception:
        return []
    if not results:
        return []

    output: list[VisionDetection] = []
    names = results[0].names or {}
    boxes = results[0].boxes
    if boxes is None:
        return output

    for box in boxes:
        cls_id = int(box.cls.item())
        label = str(names.get(cls_id, cls_id)).lower()
        conf = float(box.conf.item())
        output.append(VisionDetection(label=label, confidence=conf))
    return output


def detect_labels(model, width: int, height: int) -> list[VisionDetection]:
    """Run YOLO on a blank frame (dev fallback when no camera frames arrive)."""
    if model is None or width < 1 or height < 1:
        return []
    try:
        import numpy as np
    except ImportError:
        return []

    frame = np.zeros((height, width, 3), dtype=np.uint8)
    return detect_in_frame(model, frame)
