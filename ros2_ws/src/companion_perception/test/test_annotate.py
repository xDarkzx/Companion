"""Unit tests for drawing result boxes onto frames."""
from companion_perception.annotate import BOX_COLOUR, draw_boxes
from companion_vision.types import Box, Located
import numpy as np


def test_box_outline_is_drawn_and_the_inside_left_alone():
    rgb = np.zeros((50, 50, 3), dtype=np.uint8)
    out = draw_boxes(rgb, [Located('mug', 0.9, Box(10.0, 10.0, 40.0, 40.0), None)])
    assert out[10, 25].tolist() == list(BOX_COLOUR)
    assert out[25, 25].tolist() == [0, 0, 0]
    assert rgb.sum() == 0  # the input frame is not modified


def test_boxes_touching_the_edge_are_clipped():
    rgb = np.zeros((20, 20, 3), dtype=np.uint8)
    out = draw_boxes(rgb, [Located('mug', 0.9, Box(-5.0, -5.0, 30.0, 30.0), None)])
    assert out[0, 10].tolist() == list(BOX_COLOUR)
