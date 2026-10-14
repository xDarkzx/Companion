"""Format detection batches for the desktop vision preview overlay."""
from __future__ import annotations

from companion_interfaces.msg import Detection

IGNORED_LABELS = frozenset({
    'idle',
    'none',
    'camera_ready',
    'waiting_for_camera',
})


def format_detection_lines(detections: list[Detection]) -> list[str]:
    """Return human-readable detection lines for the preview panel."""
    lines: list[str] = []
    for det in detections:
        label = det.label.strip().lower()
        if label in IGNORED_LABELS:
            continue
        pct = int(round(float(det.confidence) * 100))
        lines.append(f'{det.label} ({pct}%)')

    if lines:
        return lines[:8]

    if detections:
        return [detections[0].label]
    return ['no detections']
