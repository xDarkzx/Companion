import sys

from companion_vision.backends.fake import FakeDetector
from companion_vision.detector import (
    DetectorLoadError,
    load_detector,
    nms,
    normalize_queries,
)
from companion_vision.types import Box, Detection2D
import numpy as np
import pytest

FRAME = np.zeros((480, 640, 3), dtype=np.uint8)


def test_queries_are_trimmed_lowercased_and_deduplicated():
    assert normalize_queries(['  Red  Mug ', 'red mug', 'Dog']) == ('red mug', 'dog')


def test_a_query_with_no_words_is_rejected():
    with pytest.raises(ValueError, match='empty query'):
        normalize_queries(['  ', ''])
    with pytest.raises(ValueError, match='empty query'):
        normalize_queries([])


def test_box_iou():
    a = Box(0.0, 0.0, 10.0, 10.0)
    assert a.iou(a) == pytest.approx(1.0)
    assert a.iou(Box(5.0, 0.0, 15.0, 10.0)) == pytest.approx(50.0 / 150.0)
    assert a.iou(Box(20.0, 20.0, 30.0, 30.0)) == 0.0


def test_nms_drops_overlapping_duplicates_of_the_same_label():
    keep = Detection2D('mug', 0.9, Box(0.0, 0.0, 10.0, 10.0))
    duplicate = Detection2D('mug', 0.6, Box(1.0, 1.0, 11.0, 11.0))
    other_label = Detection2D('cup', 0.5, Box(1.0, 1.0, 11.0, 11.0))
    elsewhere = Detection2D('mug', 0.4, Box(50.0, 50.0, 60.0, 60.0))
    result = nms([duplicate, keep, other_label, elsewhere], iou_threshold=0.5)
    assert result == [keep, other_label, elsewhere]


def test_fake_detector_finds_known_labels_at_the_image_centre():
    detector = FakeDetector(known_labels=('mug',))
    [det] = detector.detect(FRAME, ['mug', 'unicorn'])
    assert det.label == 'mug'
    assert det.box.center == (320.0, 240.0)


def test_fake_detector_honours_a_script():
    scripted = Detection2D('dog', 0.7, Box(1.0, 2.0, 3.0, 4.0))
    detector = FakeDetector(script={'dog': [scripted]})
    assert detector.detect(FRAME, ['dog']) == [scripted]


def test_load_detector_returns_the_fake_backend():
    assert load_detector('fake', device='cpu').name == 'fake'


def test_unknown_backend_is_a_load_error():
    with pytest.raises(DetectorLoadError, match='unknown detector backend'):
        load_detector('yolo', device='cpu')


def test_missing_model_libraries_are_a_load_error_not_a_silent_fallback(monkeypatch):
    monkeypatch.setitem(sys.modules, 'transformers', None)
    with pytest.raises(DetectorLoadError, match='owlv2'):
        load_detector('owlv2', device='cpu')
