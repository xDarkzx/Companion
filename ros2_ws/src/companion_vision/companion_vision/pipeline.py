"""Find named objects in a frame and place them in 3D: detect, then depth, then locate."""
from __future__ import annotations

from collections.abc import Sequence
import time

from companion_vision.depth import DepthSource
from companion_vision.detector import Detector
from companion_vision.localize import align_depth, locate
from companion_vision.types import Intrinsics, Located
import numpy as np


class Finder:
    """Run one detector and one depth source over a frame and return located objects."""

    def __init__(
        self, detector: Detector, depth: DepthSource, intrinsics: Intrinsics | None
    ) -> None:
        """Hold the stages; intrinsics may arrive later via set_intrinsics."""
        self._detector = detector
        self._depth = depth
        self._intrinsics = intrinsics
        self.timings: dict[str, float] = {}

    def set_intrinsics(self, intrinsics: Intrinsics | None) -> None:
        """Update the camera model, e.g. when CameraInfo first arrives."""
        self._intrinsics = intrinsics

    def find(
        self,
        rgb: np.ndarray,
        queries: Sequence[str],
        sensor_depth: np.ndarray | None = None,
    ) -> list[Located]:
        """Return objects matching the queries, best first; depth is computed only if needed."""
        start = time.perf_counter()
        detections = self._detector.detect(rgb, queries)
        detected = time.perf_counter()

        depth_m = None
        if detections:
            depth_m = self._depth.depth(rgb, sensor_depth)
            if depth_m is not None:
                depth_m = align_depth(depth_m, rgb.shape[:2])
        measured = time.perf_counter()

        located = [locate(det, depth_m, self._intrinsics) for det in detections]
        located.sort(key=lambda item: item.score, reverse=True)
        done = time.perf_counter()

        self.timings = {
            'detect': (detected - start) * 1000.0,
            'depth': (measured - detected) * 1000.0,
            'locate': (done - measured) * 1000.0,
        }
        return located
