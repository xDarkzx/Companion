"""The detector contract: an RGB image and text queries in, scored boxes out."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from companion_vision.types import Detection2D
import numpy as np

DEFAULT_SCORE_THRESHOLD = 0.2
DEFAULT_TOP_K = 20
NMS_IOU = 0.5


class DetectorLoadError(RuntimeError):
    """A requested detector could not be loaded; callers must not fall back silently."""


class Detector(Protocol):
    """Anything that finds objects named by free-text queries in an RGB image."""

    name: str

    def detect(self, rgb: np.ndarray, queries: Sequence[str]) -> list[Detection2D]:
        """Return detections for the queries, each labelled with the query it answers."""
        ...


def normalize_queries(queries: Sequence[str]) -> tuple[str, ...]:
    """Trim, lowercase and de-duplicate queries; raise ValueError if none has any words."""
    seen: dict[str, None] = {}
    for query in queries:
        cleaned = ' '.join(query.lower().split())
        if cleaned:
            seen.setdefault(cleaned, None)
    if not seen:
        raise ValueError('empty query')
    return tuple(seen)


def nms(detections: Sequence[Detection2D], iou_threshold: float = NMS_IOU) -> list[Detection2D]:
    """Per-label non-maximum suppression, returning survivors in descending score order."""
    kept: list[Detection2D] = []
    for det in sorted(detections, key=lambda d: d.score, reverse=True):
        if all(k.label != det.label or k.box.iou(det.box) < iou_threshold for k in kept):
            kept.append(det)
    return kept


def finalize(
    detections: Sequence[Detection2D],
    score_threshold: float,
    top_k: int = DEFAULT_TOP_K,
) -> list[Detection2D]:
    """Apply the score threshold, NMS and the top-k cap shared by every real backend."""
    confident = [d for d in detections if d.score >= score_threshold]
    return nms(confident)[:top_k]


def load_detector(
    name: str,
    *,
    device: str,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    revision: str | None = None,
) -> Detector:
    """Build the named backend, raising DetectorLoadError with the cause if it cannot load."""
    if name == 'fake':
        from companion_vision.backends.fake import FakeDetector

        return FakeDetector()
    if name == 'owlv2':
        from companion_vision.backends.owlv2 import OwlV2Detector as backend
    elif name == 'grounding_dino':
        from companion_vision.backends.grounding_dino import GroundingDinoDetector as backend
    else:
        raise DetectorLoadError(f'unknown detector backend: {name!r}')
    try:
        return backend(device=device, score_threshold=score_threshold, revision=revision)
    except (ImportError, OSError, ValueError) as exc:
        raise DetectorLoadError(f'{name} failed to load: {exc}') from exc
