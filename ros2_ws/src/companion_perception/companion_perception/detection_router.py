"""Map vision detections to optional behavior hints."""
from __future__ import annotations

from companion_interfaces.msg import Detection

PERSON_LABELS = frozenset({'person', 'human'})
DOG_LABELS = frozenset({'dog'})


def primary_target(detections: list[Detection], min_confidence: float = 0.4) -> str | None:
    """Return the highest-confidence person or dog label, if any."""
    best_label: str | None = None
    best_score = min_confidence
    for det in detections:
        label = det.label.strip().lower()
        score = float(det.confidence)
        if score < min_confidence:
            continue
        if label not in PERSON_LABELS and label not in DOG_LABELS:
            continue
        if score >= best_score:
            best_score = score
            best_label = label
    return best_label


def behavior_hint(detections: list[Detection], min_confidence: float = 0.4) -> str | None:
    """Suggest follow or play_with_dog from detections (None if no action)."""
    target = primary_target(detections, min_confidence)
    if target in DOG_LABELS:
        return 'play_with_dog'
    if target in PERSON_LABELS:
        return 'follow'
    return None
