"""Vision label helpers (mirrors companion_perception/detection_router contract)."""
from __future__ import annotations

from companion_interfaces.msg import Detection

PERSON_LABELS = frozenset({'person', 'human'})


def person_confidence(detections: list[Detection], min_confidence: float = 0.4) -> float:
    """Return best person confidence, or 0.0 when none."""
    best = 0.0
    for det in detections:
        label = det.label.strip().lower()
        if label not in PERSON_LABELS:
            continue
        score = float(det.confidence)
        if score >= min_confidence and score > best:
            best = score
    return best
