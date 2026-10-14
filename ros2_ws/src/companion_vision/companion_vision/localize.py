"""
Turn a 2D detection plus a depth map into a 3D point in the camera optical frame.

The optical frame follows ROS REP 103: x right, y down, z forward, in metres.
"""
from __future__ import annotations

from companion_vision.types import Box, Detection2D, Intrinsics, Located, Point3
import numpy as np

MIN_DEPTH_M = 0.1
MAX_DEPTH_M = 10.0
MIN_VALID_PIXELS = 20
CENTRAL_FRACTION = 0.5


def central_region(box: Box, frac: float = CENTRAL_FRACTION) -> Box:
    """Shrink a box around its centre so background at the edges is left out."""
    margin_x = box.width * (1.0 - frac) / 2.0
    margin_y = box.height * (1.0 - frac) / 2.0
    return Box(box.x0 + margin_x, box.y0 + margin_y, box.x1 - margin_x, box.y1 - margin_y)


def box_depth(
    depth_m: np.ndarray,
    box: Box,
    *,
    min_m: float = MIN_DEPTH_M,
    max_m: float = MAX_DEPTH_M,
    min_valid: int = MIN_VALID_PIXELS,
) -> float | None:
    """Median depth over the centre of the box, or None when too few pixels are trustworthy."""
    height, width = depth_m.shape[:2]
    region = central_region(box).clip(width, height)
    patch = depth_m[int(region.y0):int(np.ceil(region.y1)), int(region.x0):int(np.ceil(region.x1))]
    values = patch[np.isfinite(patch)]
    values = values[(values >= min_m) & (values <= max_m)]
    if values.size < min_valid:
        return None
    return float(np.median(values))


def back_project(u: float, v: float, z: float, k: Intrinsics) -> Point3:
    """Pinhole back-projection of pixel (u, v) at depth z."""
    return ((u - k.cx) * z / k.fx, (v - k.cy) * z / k.fy, z)


def align_depth(depth_m: np.ndarray, rgb_shape: tuple[int, int]) -> np.ndarray:
    """Resize depth to the RGB resolution with nearest-neighbour sampling (no invented values)."""
    target_h, target_w = rgb_shape
    src_h, src_w = depth_m.shape[:2]
    if (src_h, src_w) == (target_h, target_w):
        return depth_m
    rows = (np.arange(target_h) * src_h // target_h).astype(np.intp)
    cols = (np.arange(target_w) * src_w // target_w).astype(np.intp)
    return depth_m[rows[:, None], cols[None, :]]


def locate(det: Detection2D, depth_m: np.ndarray | None, k: Intrinsics | None) -> Located:
    """Attach a 3D position to a detection when depth and intrinsics allow one."""
    if depth_m is None or k is None:
        return Located.from_detection(det, None)
    z = box_depth(depth_m, det.box)
    if z is None:
        return Located.from_detection(det, None)
    u, v = det.box.center
    return Located.from_detection(det, back_project(u, v, z, k))
