from companion_vision.demo import caption, draw_overlay
from companion_vision.types import Box, Located
import numpy as np
import pytest

MUG = Located('mug', 0.91, Box(100.0, 100.0, 200.0, 220.0), (-0.3, 0.0, 1.2))


def test_caption_with_and_without_a_position():
    assert caption(MUG) == 'mug 0.91 | 1.2 m'
    assert caption(Located('mug', 0.5, MUG.box, None)) == 'mug 0.50 | no depth'


def test_overlay_draws_on_a_copy():
    cv2 = pytest.importorskip('cv2')
    assert cv2 is not None
    frame = np.zeros((300, 400, 3), dtype=np.uint8)
    out = draw_overlay(frame, [MUG])
    assert frame.sum() == 0
    assert out[100, 150].any()
    assert not out[160, 150].any()
