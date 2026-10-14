"""A deterministic detector for tests and offline launch checks; never used as a fallback."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from companion_vision.detector import normalize_queries
from companion_vision.types import Box, Detection2D
import numpy as np

DEFAULT_KNOWN_LABELS = ('mug', 'person', 'dog')
FAKE_SCORE = 0.9
BOX_FRACTION = 0.2


class FakeDetector:
    """Finds known labels at the image centre, or returns scripted detections per query."""

    name = 'fake'

    def __init__(
        self,
        known_labels: Sequence[str] = DEFAULT_KNOWN_LABELS,
        script: Mapping[str, list[Detection2D]] | None = None,
    ) -> None:
        """Configure which queries are 'visible' to the fake camera."""
        self._known = frozenset(known_labels)
        self._script = dict(script or {})

    def detect(self, rgb: np.ndarray, queries: Sequence[str]) -> list[Detection2D]:
        """Return scripted detections, or a centred box for each known label."""
        height, width = rgb.shape[:2]
        half_w, half_h = width * BOX_FRACTION / 2.0, height * BOX_FRACTION / 2.0
        cx, cy = width / 2.0, height / 2.0
        found: list[Detection2D] = []
        for query in normalize_queries(queries):
            if query in self._script:
                found.extend(self._script[query])
            elif query in self._known:
                box = Box(cx - half_w, cy - half_h, cx + half_w, cy + half_h)
                found.append(Detection2D(query, FAKE_SCORE, box))
        return found
