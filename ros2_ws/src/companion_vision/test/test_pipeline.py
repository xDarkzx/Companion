from companion_vision.backends.fake import FakeDetector
from companion_vision.depth import NoDepth, SensorDepth
from companion_vision.pipeline import Finder
from companion_vision.types import Box, Detection2D, Intrinsics
import numpy as np
import pytest

RGB = np.zeros((480, 640, 3), dtype=np.uint8)
K = Intrinsics(fx=500.0, fy=500.0, cx=320.0, cy=240.0)


def depth_at(metres: float, shape=(480, 640)) -> np.ndarray:
    return np.full(shape, int(metres * 1000), dtype=np.uint16)


def test_results_are_sorted_by_score():
    low = Detection2D('dog', 0.3, Box(0.0, 0.0, 50.0, 50.0))
    high = Detection2D('mug', 0.8, Box(100.0, 100.0, 150.0, 150.0))
    finder = Finder(FakeDetector(script={'dog': [low], 'mug': [high]}), NoDepth(), K)
    assert [r.label for r in finder.find(RGB, ['dog', 'mug'])] == ['mug', 'dog']


def test_positions_are_filled_from_sensor_depth():
    finder = Finder(FakeDetector(), SensorDepth(), K)
    [mug] = finder.find(RGB, ['mug'], sensor_depth=depth_at(1.5))
    assert mug.xyz == pytest.approx((0.0, 0.0, 1.5))


def test_missing_depth_or_intrinsics_leaves_positions_empty():
    assert Finder(FakeDetector(), SensorDepth(), K).find(RGB, ['mug'])[0].xyz is None
    no_k = Finder(FakeDetector(), SensorDepth(), None)
    assert no_k.find(RGB, ['mug'], sensor_depth=depth_at(1.5))[0].xyz is None


def test_lower_resolution_depth_is_aligned_to_the_image():
    finder = Finder(FakeDetector(), SensorDepth(), K)
    [mug] = finder.find(RGB, ['mug'], sensor_depth=depth_at(2.0, shape=(240, 320)))
    assert mug.xyz[2] == pytest.approx(2.0)


def test_nothing_found_returns_an_empty_list():
    assert Finder(FakeDetector(), SensorDepth(), K).find(RGB, ['unicorn']) == []


def test_stage_timings_are_recorded():
    finder = Finder(FakeDetector(), SensorDepth(), K)
    finder.find(RGB, ['mug'], sensor_depth=depth_at(1.0))
    assert set(finder.timings) == {'detect', 'depth', 'locate'}
    assert all(ms >= 0.0 for ms in finder.timings.values())
