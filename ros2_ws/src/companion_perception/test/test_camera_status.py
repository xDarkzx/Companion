"""Tests for camera status computation."""
from companion_perception.camera_status import compute_camera_status, STALE_NS


def test_waiting_when_no_frames():
    assert compute_camera_status(False, False, 0, 0, 1_000) == 'waiting'


def test_ready_when_both_fresh():
    now = 10_000_000_000
    assert compute_camera_status(True, True, now - 1, now - 1, now, STALE_NS) == 'ready'


def test_stale_when_frames_old():
    now = 20_000_000_000
    old = now - STALE_NS - 1
    assert compute_camera_status(True, True, old, old, now) == 'stale'


def test_rgb_only():
    now = 5_000_000_000
    assert compute_camera_status(True, False, now - 1, 0, now) == 'rgb_only'
