import sys

from companion_vision.depth import DepthLoadError, load_depth, NoDepth, SensorDepth
import numpy as np
import pytest

RGB = np.zeros((4, 6, 3), dtype=np.uint8)


def test_sensor_depth_converts_millimetres_to_metres():
    raw = np.full((4, 6), 1500, dtype=np.uint16)
    depth = SensorDepth().depth(RGB, raw)
    assert depth.dtype == np.float32
    assert depth[0, 0] == pytest.approx(1.5)


def test_sensor_depth_passes_float_metres_through():
    raw = np.full((4, 6), 2.25, dtype=np.float32)
    assert SensorDepth().depth(RGB, raw)[0, 0] == pytest.approx(2.25)


def test_sensor_depth_without_a_frame_is_none():
    assert SensorDepth().depth(RGB, None) is None


def test_no_depth_is_always_none():
    assert NoDepth().depth(RGB, np.ones((4, 6), dtype=np.float32)) is None


def test_modes_map_to_sources():
    assert isinstance(load_depth('sensor', device='cpu'), SensorDepth)
    assert isinstance(load_depth('none', device='cpu'), NoDepth)


def test_unknown_mode_is_a_load_error():
    with pytest.raises(DepthLoadError, match='unknown depth mode'):
        load_depth('lidar', device='cpu')


def test_missing_model_libraries_are_a_load_error(monkeypatch):
    monkeypatch.setitem(sys.modules, 'transformers', None)
    with pytest.raises(DepthLoadError, match='monocular'):
        load_depth('monocular', device='cpu')
