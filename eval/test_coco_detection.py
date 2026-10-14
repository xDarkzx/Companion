"""Unit tests for converting detections to COCO result records."""
from coco_detection import to_coco_results

from companion_vision.types import Box, Detection2D


def test_boxes_become_coco_xywh_with_category_ids():
    dets = [Detection2D('cat', 0.9, Box(10.0, 20.0, 50.0, 80.0)),
            Detection2D('unknown', 0.5, Box(0.0, 0.0, 1.0, 1.0))]
    records = to_coco_results(39769, dets, {'cat': 17})
    assert records == [{'image_id': 39769, 'category_id': 17,
                        'bbox': [10.0, 20.0, 40.0, 60.0], 'score': 0.9}]
