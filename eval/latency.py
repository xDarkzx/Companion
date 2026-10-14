"""Is it fast enough for a robot? Per-stage latency on fixed NYU frames.

Usage: python eval/latency.py --backend owlv2 --device cuda   (or --device cpu)
Run with nothing else using the GPU: concurrent work inflates every number.
"""
from __future__ import annotations

import argparse
import time

from common import data_dir, percentile, write_result
from companion_vision.localize import locate
from nyu_data import NYU_K, NyuLabelled, split_test_indices

FRAMES = 200
WARM_UP = 10
QUERY = 'chair'


def stage_summary(values_ms: list[float]) -> dict:
    """p50 and p95 of one stage, in milliseconds."""
    return {'p50_ms': round(percentile(values_ms, 50), 1),
            'p95_ms': round(percentile(values_ms, 95), 1)}


def run(backend: str, device: str) -> str:
    """Time detection, monocular depth and localisation separately for each frame."""
    from companion_vision.depth import load_depth
    from companion_vision.detector import load_detector

    root = data_dir()
    nyu = NyuLabelled(root / 'nyu_depth_v2_labeled.mat')
    frames = list(nyu.frames(split_test_indices(root / 'splits.mat')[:FRAMES + WARM_UP]))
    detector = load_detector(backend, device=device)
    depth = load_depth('monocular', device=device)
    stages: dict[str, list[float]] = {'detect': [], 'depth': [], 'total': []}
    for count, frame in enumerate(frames):
        start = time.perf_counter()
        detections = detector.detect(frame.rgb, [QUERY])
        detected = time.perf_counter()
        depth_m = depth.depth(frame.rgb, None)
        measured = time.perf_counter()
        for det in detections:
            locate(det, depth_m, NYU_K)
        done = time.perf_counter()
        if count < WARM_UP:
            continue
        stages['detect'].append((detected - start) * 1000.0)
        stages['depth'].append((measured - detected) * 1000.0)
        stages['total'].append((done - start) * 1000.0)
    metrics = {stage: stage_summary(values) for stage, values in stages.items()}
    module = __import__(f'companion_vision.backends.{backend}', fromlist=['MODEL_ID'])
    depth_module = __import__('companion_vision.backends.depth_anything',
                              fromlist=['MODEL_ID', 'MODEL_REVISION'])
    path = write_result(
        f'latency_{backend}_{device}', metrics,
        models={'detector': f'{module.MODEL_ID}@{module.MODEL_REVISION}',
                'monocular_depth': f'{depth_module.MODEL_ID}@{depth_module.MODEL_REVISION}'},
        settings={'backend': backend, 'device': device, 'frames': FRAMES, 'warm_up': WARM_UP,
                  'query': QUERY, 'resolution': '640x480', 'precision': 'fp32',
                  'batch': 1},
    )
    return str(path)


def main() -> None:
    """Parse arguments and time one backend on one device."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--backend', choices=['owlv2', 'grounding_dino'], required=True)
    parser.add_argument('--device', choices=['cuda', 'cpu'], required=True)
    args = parser.parse_args()
    print(run(args.backend, args.device))


if __name__ == '__main__':
    main()
