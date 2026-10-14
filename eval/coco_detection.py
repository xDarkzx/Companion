"""How well does each detector find named objects? COCO val2017, class names as text queries.

Usage: python eval/coco_detection.py --backend owlv2 [--limit 50]
Needs D:/Datasets/companion/val2017 and annotations/instances_val2017.json (see docs/EVALUATION.md).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from common import data_dir, percentile, REPO, write_result
from companion_vision.detector import load_detector
from companion_vision.types import Detection2D
import numpy as np

# Paper-style settings for comparability: a low threshold and up to 100 boxes per image.
SCORE_THRESHOLD = 0.05
TOP_K = 100
CACHE_DIR = REPO / 'eval' / '.cache'


def to_coco_results(image_id: int, detections: list[Detection2D],
                    name_to_category: dict[str, int]) -> list[dict]:
    """Convert detections to COCO result records ([x, y, w, h] boxes)."""
    records = []
    for det in detections:
        category = name_to_category.get(det.label)
        if category is None:
            continue
        box = det.box
        records.append({'image_id': image_id, 'category_id': category,
                        'bbox': [box.x0, box.y0, box.width, box.height],
                        'score': round(det.score, 5)})
    return records


def load_rgb(path: Path) -> np.ndarray:
    """Read an image file as an RGB uint8 array."""
    from PIL import Image

    with Image.open(path) as image:
        return np.asarray(image.convert('RGB'))


def run(backend: str, limit: int | None) -> Path:
    """Detect every val2017 image, score with pycocotools, and write the result file."""
    import torch
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval

    root = data_dir()
    coco = COCO(str(root / 'annotations' / 'instances_val2017.json'))
    categories = coco.loadCats(coco.getCatIds())
    names = [c['name'] for c in categories]
    name_to_category = {c['name']: c['id'] for c in categories}
    image_ids = sorted(coco.getImgIds())[:limit]

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    detector = load_detector(backend, device=device, score_threshold=SCORE_THRESHOLD, top_k=TOP_K)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f'_{limit}' if limit else ''
    cache = CACHE_DIR / f'coco_{backend}{suffix}.jsonl'
    done = {}
    if cache.exists():
        for line in cache.read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            done[row['image_id']] = row
    timings = [row['ms'] for row in done.values()]
    with cache.open('a', encoding='utf-8') as out:
        for count, image_id in enumerate(image_ids, 1):
            if image_id in done:
                continue
            info = coco.loadImgs(image_id)[0]
            rgb = load_rgb(root / 'val2017' / info['file_name'])
            start = time.perf_counter()
            detections = detector.detect(rgb, names)
            ms = (time.perf_counter() - start) * 1000.0
            row = {'image_id': image_id, 'ms': ms,
                   'results': to_coco_results(image_id, detections, name_to_category)}
            out.write(json.dumps(row) + '\n')
            done[image_id] = row
            timings.append(ms)
            if count % 250 == 0:
                print(f'{backend}: {count}/{len(image_ids)} images', flush=True)

    results = [r for image_id in image_ids for r in done[image_id]['results']]
    evaluator = COCOeval(coco, coco.loadRes(results), 'bbox')
    evaluator.params.imgIds = image_ids
    evaluator.evaluate()
    evaluator.accumulate()
    evaluator.summarize()
    stats = evaluator.stats
    metrics = {
        'images': len(image_ids),
        'AP': round(float(stats[0]), 4),
        'AP50': round(float(stats[1]), 4),
        'AP75': round(float(stats[2]), 4),
        'AP_small': round(float(stats[3]), 4),
        'AP_medium': round(float(stats[4]), 4),
        'AP_large': round(float(stats[5]), 4),
        'ms_per_image_p50': round(percentile(timings, 50), 1),
    }
    revision = getattr(__import__(f'companion_vision.backends.{backend}',
                                  fromlist=['MODEL_REVISION']), 'MODEL_REVISION')
    model_id = getattr(__import__(f'companion_vision.backends.{backend}',
                                  fromlist=['MODEL_ID']), 'MODEL_ID')
    return write_result(
        f'coco_{backend}{suffix}', metrics,
        models={'detector': f'{model_id}@{revision}'},
        settings={'dataset': 'COCO val2017', 'queries': 'the 80 COCO class names, unmodified',
                  'score_threshold': SCORE_THRESHOLD, 'max_boxes_per_image': TOP_K,
                  'nms_iou': 0.5, 'precision': 'fp32'},
    )


def main() -> None:
    """Parse arguments and run one backend."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--backend', choices=['owlv2', 'grounding_dino'], required=True)
    parser.add_argument('--limit', type=int, default=None, help='first N images only (smoke run)')
    args = parser.parse_args()
    print(run(args.backend, args.limit))


if __name__ == '__main__':
    main()
