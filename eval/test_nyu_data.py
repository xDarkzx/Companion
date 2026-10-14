"""Unit tests for NYU Depth V2 ground-truth helpers (synthetic arrays, no dataset needed)."""
from companion_vision.types import Intrinsics
import numpy as np
from nyu_data import gt_centroid, instances_in_frame, mask_box, VALID_REGION
import pytest

K = Intrinsics(fx=500.0, fy=500.0, cx=320.0, cy=240.0)


def test_mask_box_is_inclusive_of_the_last_pixel():
    mask = np.zeros((480, 640), dtype=bool)
    mask[100:150, 200:260] = True
    box = mask_box(mask)
    assert (box.x0, box.y0, box.x1, box.y1) == (200.0, 100.0, 260.0, 150.0)


def test_gt_centroid_is_the_median_3d_point_of_the_mask():
    depth = np.full((480, 640), 2.0, dtype=np.float32)
    mask = np.zeros((480, 640), dtype=bool)
    mask[230:251, 310:331] = True  # centred on the principal point
    x, y, z = gt_centroid(mask, depth, K)
    assert (x, y, z) == pytest.approx((0.0, 0.0, 2.0), abs=1e-6)


def test_instances_keep_large_whole_objects_of_chosen_classes():
    labels = np.zeros((480, 640), dtype=np.uint16)
    instances = np.zeros((480, 640), dtype=np.uint8)
    top, left, bottom, right = VALID_REGION
    labels[200:260, 200:260], instances[200:260, 200:260] = 5, 1      # chair, big, inside
    labels[300:305, 300:305], instances[300:305, 300:305] = 5, 2      # chair, too small
    labels[top:top + 40, 300:360], instances[top:top + 40, 300:360] = 5, 3  # touches the edge
    labels[100:160, 400:460], instances[100:160, 400:460] = 7, 1      # class not chosen
    found = instances_in_frame(labels, instances, {5: 'chair'})
    assert [name for name, _mask in found] == ['chair']
    assert found[0][1].sum() == 60 * 60
