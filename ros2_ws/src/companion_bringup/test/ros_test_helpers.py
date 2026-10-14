"""Shared helpers for Companion launch_testing integration tests."""
from __future__ import annotations

from collections.abc import Callable
import math
import os
import time

from ament_index_python.packages import get_package_share_directory
from companion_memory.places_contract import REFERENCE_PLACES
import rclpy
from rclpy.node import Node
from rclpy.publisher import Publisher

COORD_TOLERANCE = 0.01


def config_path(name: str) -> str:
    """Return an installed bringup config file path."""
    share = get_package_share_directory('companion_bringup')
    return os.path.join(share, 'config', name)


def warm_up_dds(node: Node, seconds: float = 2.0) -> None:
    """Spin briefly so subscriptions discover publishers before assertions."""
    deadline = time.time() + seconds
    while time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)


def spin_until(
    node: Node,
    predicate: Callable[[], bool],
    timeout_sec: float = 12.0,
    period_sec: float = 0.1,
) -> bool:
    """Spin the node until predicate is true or timeout."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=period_sec)
        if predicate():
            return True
    return False


def wait_for_subscribers(pub: Publisher, min_count: int = 1, timeout_sec: float = 10.0) -> bool:
    """Wait until at least min_count subscribers connect to a publisher."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if pub.get_subscription_count() >= min_count:
            return True
        time.sleep(0.05)
    return False


def assert_pose_near(
    actual_x, actual_y, expected_x, expected_y, tol: float = COORD_TOLERANCE,
) -> None:
    """Assert map coordinates match within tolerance."""
    assert abs(actual_x - expected_x) <= tol, f'x {actual_x} != {expected_x}'
    assert abs(actual_y - expected_y) <= tol, f'y {actual_y} != {expected_y}'


def assert_place_xy(
    name: str, actual_x: float, actual_y: float, tol: float = COORD_TOLERANCE,
) -> None:
    """Assert coordinates match documented places_contract ground truth."""
    ref = REFERENCE_PLACES[name]
    assert_pose_near(actual_x, actual_y, ref['x'], ref['y'], tol)


def expected_follow_standoff_xy(
    place_name: str,
    standoff_m: float,
) -> tuple[float, float]:
    """Return expected map x/y after standoff_from_place math."""
    ref = REFERENCE_PLACES[place_name]
    yaw = ref['yaw']
    x = ref['x'] + math.cos(yaw) * standoff_m
    y = ref['y'] + math.sin(yaw) * standoff_m
    return x, y


def require_subscribers(pub: Publisher, label: str = 'topic') -> None:
    """Fail fast when the graph is not wired (prevents false passes)."""
    ok = wait_for_subscribers(pub)
    assert ok, f'no subscriber connected to {label} — test would be invalid'
