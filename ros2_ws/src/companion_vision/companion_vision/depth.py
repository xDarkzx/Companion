"""Depth sources: a depth camera, a monocular depth model, or none. All return metres."""
from __future__ import annotations

from typing import Protocol

import numpy as np

MILLIMETRES_TO_METRES = 0.001


class DepthLoadError(RuntimeError):
    """A requested depth source could not be loaded; callers must not fall back silently."""


class DepthSource(Protocol):
    """Produce a depth map in metres aligned to the RGB frame, or None."""

    def depth(self, rgb: np.ndarray, sensor: np.ndarray | None) -> np.ndarray | None:
        """Return depth in metres for this frame, or None when none is available."""
        ...


class SensorDepth:
    """Use the depth camera's frame: uint16 millimetres (ROS 16UC1) or float32 metres (32FC1)."""

    def __init__(self, scale: float = MILLIMETRES_TO_METRES) -> None:
        """Set the scale applied to integer depth images."""
        self._scale = scale

    def depth(self, rgb: np.ndarray, sensor: np.ndarray | None) -> np.ndarray | None:
        """Convert the sensor frame to float32 metres."""
        if sensor is None:
            return None
        if np.issubdtype(sensor.dtype, np.integer):
            return sensor.astype(np.float32) * np.float32(self._scale)
        return sensor.astype(np.float32, copy=False)


class NoDepth:
    """No depth at all: detections are reported without a 3D position."""

    def depth(self, rgb: np.ndarray, sensor: np.ndarray | None) -> np.ndarray | None:
        """Return None: this source never has depth."""
        return None


def load_depth(mode: str, *, device: str, revision: str | None = None) -> DepthSource:
    """Build the depth source for a mode: 'sensor', 'monocular' or 'none'."""
    if mode == 'sensor':
        return SensorDepth()
    if mode == 'none':
        return NoDepth()
    if mode != 'monocular':
        raise DepthLoadError(f'unknown depth mode: {mode!r}')
    try:
        from companion_vision.backends.depth_anything import MonocularDepth

        return MonocularDepth(device=device, revision=revision)
    except (ImportError, OSError, ValueError) as exc:
        raise DepthLoadError(f'monocular depth failed to load: {exc}') from exc
