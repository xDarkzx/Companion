"""Real-weight smoke tests: run with COMPANION_MODEL_TESTS=1 on a machine with the models."""
import io
import urllib.request

from companion_vision.detector import load_detector
from companion_vision.types import Box
import numpy as np
import pytest

# COCO val2017 image 39769: two cats on a pink blanket. Boxes are its ground-truth annotations.
COCO_CATS = 'http://images.cocodataset.org/val2017/000000039769.jpg'
LEFT_CAT = Box(17.5, 54.4, 318.7, 469.4)
RIGHT_CAT = Box(347.5, 25.6, 640.0, 369.4)


def coco_cats() -> np.ndarray:
    from PIL import Image

    with urllib.request.urlopen(COCO_CATS, timeout=30) as response:
        return np.asarray(Image.open(io.BytesIO(response.read())).convert('RGB'))


@pytest.mark.models
@pytest.mark.parametrize('backend', ['owlv2', 'grounding_dino'])
def test_backend_finds_both_cats(backend):
    import torch

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    detector = load_detector(backend, device=device, score_threshold=0.3)
    cats = [d for d in detector.detect(coco_cats(), ['cat', 'remote control']) if d.label == 'cat']
    assert len(cats) >= 2
    for expected in (LEFT_CAT, RIGHT_CAT):
        assert max(c.box.iou(expected) for c in cats) > 0.7
