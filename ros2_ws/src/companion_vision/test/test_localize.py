from companion_vision.localize import (
    align_depth,
    back_project,
    box_depth,
    central_region,
    locate,
)
from companion_vision.types import Box, Detection2D, Intrinsics
import numpy as np
import pytest

K = Intrinsics(fx=500.0, fy=500.0, cx=320.0, cy=240.0)


def plane(depth_m: float, shape=(480, 640)) -> np.ndarray:
    return np.full(shape, depth_m, dtype=np.float32)


def test_central_region_keeps_the_middle_half():
    assert central_region(Box(0.0, 0.0, 100.0, 40.0)) == Box(25.0, 10.0, 75.0, 30.0)


def test_box_depth_of_a_flat_plane():
    assert box_depth(plane(2.0), Box(100.0, 100.0, 200.0, 200.0)) == pytest.approx(2.0)


def test_background_at_the_box_edges_does_not_move_the_estimate():
    depth = plane(5.0)
    depth[120:180, 120:180] = 1.2  # the object fills the centre; the wall shows at the edges
    assert box_depth(depth, Box(100.0, 100.0, 200.0, 200.0)) == pytest.approx(1.2)


def test_missing_depth_is_reported_as_none():
    zeros = plane(0.0)
    nans = plane(float('nan'))
    box = Box(100.0, 100.0, 200.0, 200.0)
    assert box_depth(zeros, box) is None
    assert box_depth(nans, box) is None


def test_out_of_range_depth_is_ignored():
    box = Box(100.0, 100.0, 200.0, 200.0)
    assert box_depth(plane(0.05), box) is None
    assert box_depth(plane(25.0), box) is None


def test_too_few_valid_pixels_gives_none():
    depth = plane(0.0)
    depth[150, 150] = 1.0
    assert box_depth(depth, Box(100.0, 100.0, 200.0, 200.0)) is None


def test_box_partly_outside_the_image_is_clipped():
    assert box_depth(plane(3.0), Box(600.0, 400.0, 700.0, 520.0)) == pytest.approx(3.0)


def test_box_fully_outside_the_image_gives_none():
    assert box_depth(plane(3.0), Box(700.0, 500.0, 800.0, 600.0)) is None


def test_back_projection_matches_the_pinhole_model():
    x, y, z = back_project(570.0, 140.0, 2.0, K)
    assert (x, y, z) == pytest.approx((1.0, -0.4, 2.0))


def test_align_depth_resizes_to_the_rgb_resolution():
    small = np.zeros((240, 320), dtype=np.float32)
    small[:, 160:] = 4.0
    aligned = align_depth(small, (480, 640))
    assert aligned.shape == (480, 640)
    assert aligned[0, 0] == 0.0
    assert aligned[0, 639] == 4.0


def test_align_depth_leaves_matching_depth_untouched():
    depth = plane(1.0)
    assert align_depth(depth, (480, 640)) is depth


def test_locate_gives_a_3d_point_at_the_box_centre():
    det = Detection2D('mug', 0.8, Box(520.0, 90.0, 620.0, 190.0))
    located = locate(det, plane(2.0), K)
    assert located.xyz == pytest.approx((1.0, -0.4, 2.0))


def test_locate_without_depth_or_intrinsics_has_no_position():
    det = Detection2D('mug', 0.8, Box(520.0, 90.0, 620.0, 190.0))
    assert locate(det, None, K).xyz is None
    assert locate(det, plane(2.0), None).xyz is None
    assert locate(det, plane(0.0), K).xyz is None
