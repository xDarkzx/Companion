import math

from companion_vision.types import Box, Detection2D, Intrinsics, Located
import pytest


def test_box_geometry():
    box = Box(10.0, 20.0, 50.0, 100.0)
    assert (box.width, box.height, box.area) == (40.0, 80.0, 3200.0)
    assert box.center == (30.0, 60.0)


def test_box_rejects_inverted_corners():
    with pytest.raises(ValueError):
        Box(50.0, 0.0, 10.0, 10.0)
    with pytest.raises(ValueError):
        Box(0.0, 50.0, 10.0, 10.0)


def test_box_clip_keeps_it_inside_the_image():
    assert Box(-5.0, -5.0, 700.0, 300.0).clip(640, 480) == Box(0.0, 0.0, 640.0, 300.0)


def test_box_clip_of_a_box_fully_outside_is_empty():
    clipped = Box(700.0, 10.0, 800.0, 20.0).clip(640, 480)
    assert clipped.area == 0.0


def test_intrinsics_from_a_90_degree_field_of_view():
    k = Intrinsics.from_fov(640, 480, 90.0)
    assert k.fx == pytest.approx(320.0)
    assert k.fy == pytest.approx(320.0)
    assert (k.cx, k.cy) == (320.0, 240.0)


def test_located_distance():
    det = Detection2D('mug', 0.9, Box(0.0, 0.0, 1.0, 1.0))
    located = Located.from_detection(det, (3.0, 0.0, 4.0))
    assert located.distance == pytest.approx(5.0)
    assert located.label == 'mug'


def test_located_without_position_has_no_distance():
    det = Detection2D('mug', 0.9, Box(0.0, 0.0, 1.0, 1.0))
    assert Located.from_detection(det, None).distance is None
    assert not math.isnan(det.score)
