"""Pure camera health logic for MentorPi depth camera watch node."""
from __future__ import annotations

STALE_NS = int(5.0 * 1e9)


def compute_camera_status(
    rgb_seen: bool,
    depth_seen: bool,
    last_rgb_ns: int,
    last_depth_ns: int,
    now_ns: int,
    stale_ns: int = STALE_NS,
) -> str:
    """Return status label from frame freshness (no ROS dependencies)."""
    rgb_ok = rgb_seen and (now_ns - last_rgb_ns) < stale_ns
    depth_ok = depth_seen and (now_ns - last_depth_ns) < stale_ns

    if rgb_ok and depth_ok:
        return 'ready'
    if rgb_ok:
        return 'rgb_only'
    if depth_ok:
        return 'depth_only'
    if rgb_seen or depth_seen:
        return 'stale'
    return 'waiting'
