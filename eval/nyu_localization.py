"""How accurate are the 3D positions? NYU Depth V2 labelled test split (654 indoor frames).

For each household object in the frame the detector is asked for its class name. Matched
detections (IoU >= 0.5) are placed in 3D twice: with the raw depth-camera frame (holes and all)
and with monocular depth from the RGB image alone. Each is compared against the object's
ground-truth position from the in-filled depth and its segmentation mask.

Usage: python eval/nyu_localization.py --backend owlv2 [--limit 50]
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import math
from pathlib import Path

from common import data_dir, write_result
from companion_vision.detector import DEFAULT_SCORE_THRESHOLD, DEFAULT_TOP_K, load_detector
from companion_vision.localize import locate
from companion_vision.types import Box, Detection2D
import numpy as np
from nyu_data import (
    CLASSES,
    gt_centroid,
    instances_in_frame,
    mask_box,
    NYU_K,
    NyuLabelled,
    split_test_indices,
    VALID_REGION,
)

MATCH_IOU = 0.5
DEPTH_RANGE_M = (0.1, 10.0)


def greedy_match(preds: list[Detection2D], truths: list[Box],
                 iou_threshold: float = MATCH_IOU) -> list[tuple[int, int]]:
    """Pair predictions (highest score first) with unused ground-truth boxes at IoU >= threshold."""
    pairs: list[tuple[int, int]] = []
    used: set[int] = set()
    for p_index in sorted(range(len(preds)), key=lambda i: preds[i].score, reverse=True):
        best, best_iou = None, iou_threshold
        for t_index, truth in enumerate(truths):
            if t_index in used:
                continue
            iou = preds[p_index].box.iou(truth)
            if iou >= best_iou:
                best, best_iou = t_index, iou
        if best is not None:
            used.add(best)
            pairs.append((p_index, best))
    return pairs


def depth_metrics(pred: np.ndarray, gt: np.ndarray, valid: np.ndarray) -> tuple[float, float]:
    """AbsRel and delta < 1.25 over valid pixels (standard monocular depth metrics)."""
    p, g = pred[valid].astype(np.float64), gt[valid].astype(np.float64)
    abs_rel = float(np.mean(np.abs(p - g) / g))
    delta1 = float(np.mean(np.maximum(p / g, g / p) < 1.25))
    return abs_rel, delta1


def scale_bias(pred: np.ndarray, gt: np.ndarray, valid: np.ndarray) -> float:
    """Median of truth / prediction: 1.0 means no systematic scale error."""
    return float(np.median(gt[valid] / pred[valid]))


def summarize_errors(errors_m: list[float]) -> dict:
    """Median error in cm and the share of objects within 10 cm and 25 cm."""
    if not errors_m:
        return {'objects': 0, 'median_error_cm': None, 'within_10cm': None, 'within_25cm': None}
    values = np.asarray(errors_m)
    return {
        'objects': int(values.size),
        'median_error_cm': round(float(np.median(values)) * 100.0, 1),
        'within_10cm': round(float(np.mean(values <= 0.10)), 3),
        'within_25cm': round(float(np.mean(values <= 0.25)), 3),
    }


def distance(a, b) -> float:
    """Euclidean distance between two 3D points."""
    return math.dist(a, b)


def run(backend: str, limit: int | None) -> Path:
    """Evaluate one detector on the NYU test split and write the result file."""
    import torch

    from companion_vision.depth import load_depth

    root = data_dir()
    nyu = NyuLabelled(root / 'nyu_depth_v2_labeled.mat')
    class_ids = nyu.class_ids()
    indices = split_test_indices(root / 'splits.mat')[:limit]
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    detector = load_detector(backend, device=device)
    mono = load_depth('monocular', device=device)
    top, left, bottom, right = VALID_REGION

    truths_total: dict[str, int] = defaultdict(int)
    matched: dict[str, int] = defaultdict(int)
    errors = {'sensor': [], 'monocular': []}
    sensor_unplaced = 0
    abs_rels, delta1s, biases, scaled_abs_rels = [], [], [], []
    for count, frame in enumerate(nyu.frames(indices), 1):
        mono_depth = mono.depth(frame.rgb, None)
        valid = np.zeros_like(frame.depth, dtype=bool)
        valid[top:bottom, left:right] = True
        valid &= (frame.depth > DEPTH_RANGE_M[0]) & (frame.depth < DEPTH_RANGE_M[1])
        abs_rel, delta1 = depth_metrics(mono_depth, frame.depth, valid)
        abs_rels.append(abs_rel)
        delta1s.append(delta1)
        bias = scale_bias(mono_depth, frame.depth, valid)
        biases.append(bias)
        scaled_abs_rels.append(depth_metrics(mono_depth * bias, frame.depth, valid)[0])

        objects = instances_in_frame(frame.labels, frame.instances, class_ids)
        if not objects:
            continue
        present = sorted({name for name, _mask in objects})
        detections = detector.detect(frame.rgb, present)
        for name in present:
            masks = [mask for obj_name, mask in objects if obj_name == name]
            truths_total[name] += len(masks)
            preds = [d for d in detections if d.label == name]
            for p_index, t_index in greedy_match(preds, [mask_box(m) for m in masks]):
                matched[name] += 1
                truth = gt_centroid(masks[t_index], frame.depth, NYU_K)
                sensor = locate(preds[p_index], frame.raw_depth, NYU_K).xyz
                monocular = locate(preds[p_index], mono_depth, NYU_K).xyz
                if sensor is None:
                    sensor_unplaced += 1
                else:
                    errors['sensor'].append(distance(sensor, truth))
                if monocular is not None:
                    errors['monocular'].append(distance(monocular, truth))
        if count % 100 == 0:
            print(f'{backend}: {count}/{len(indices)} frames', flush=True)

    total = sum(truths_total.values())
    hits = sum(matched.values())
    metrics = {
        'frames': len(indices),
        'objects': total,
        'detection_recall_iou50': round(hits / total, 3) if total else None,
        'per_class_recall': {name: round(matched[name] / truths_total[name], 3)
                             for name in CLASSES if truths_total[name]},
        'sensor_depth': {**summarize_errors(errors['sensor']), 'unplaced': sensor_unplaced},
        'monocular_depth': summarize_errors(errors['monocular']),
        'monocular_depth_map': {
            'abs_rel': round(float(np.mean(abs_rels)), 4),
            'delta1': round(float(np.mean(delta1s)), 4),
            'median_scale_bias': round(float(np.median(biases)), 3),
            'abs_rel_after_per_frame_median_scaling': round(float(np.mean(scaled_abs_rels)), 4),
        },
    }
    detector_module = __import__(f'companion_vision.backends.{backend}',
                                 fromlist=['MODEL_ID', 'MODEL_REVISION'])
    depth_module = __import__('companion_vision.backends.depth_anything',
                              fromlist=['MODEL_ID', 'MODEL_REVISION'])
    suffix = f'_{limit}' if limit else ''
    return write_result(
        f'nyu_localization_{backend}{suffix}', metrics,
        models={'detector': f'{detector_module.MODEL_ID}@{detector_module.MODEL_REVISION}',
                'monocular_depth': f'{depth_module.MODEL_ID}@{depth_module.MODEL_REVISION}'},
        settings={'dataset': 'NYU Depth V2 labelled, official test split',
                  'classes': list(CLASSES), 'match_iou': MATCH_IOU,
                  'score_threshold': DEFAULT_SCORE_THRESHOLD, 'max_boxes': DEFAULT_TOP_K,
                  'min_object_pixels': 500, 'valid_region': 'Eigen crop',
                  'ground_truth': 'median 3D point of the object mask on in-filled depth',
                  'sensor_path': 'rawDepths (holes kept)', 'precision': 'fp32'},
    )


def main() -> None:
    """Parse arguments and run one backend."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--backend', choices=['owlv2', 'grounding_dino'], required=True)
    parser.add_argument('--limit', type=int, default=None, help='first N frames only')
    args = parser.parse_args()
    print(run(args.backend, args.limit))


if __name__ == '__main__':
    main()
