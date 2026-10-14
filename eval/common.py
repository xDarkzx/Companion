"""Shared helpers for the evaluation scripts: data location, provenance and statistics."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess

import numpy as np

REPO = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO / 'eval' / 'results'
DEFAULT_DATA_DIR = Path('D:/Datasets/companion')


def data_dir() -> Path:
    """Where downloaded datasets live (never inside the repo); override with COMPANION_DATA."""
    return Path(os.environ.get('COMPANION_DATA', DEFAULT_DATA_DIR))


def git_commit() -> str:
    """Commit the results were produced from, marked dirty if the tree had changes."""
    try:
        sha = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(['git', 'status', '--porcelain', '--', 'ros2_ws', 'eval'],
                               cwd=REPO, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return 'unknown'
    return f'{sha}-dirty' if dirty.strip() else sha


def device_name() -> str:
    """Human-readable compute device: the GPU name, or the CPU."""
    try:
        import torch

        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except ImportError:
        pass
    return platform.processor() or platform.machine()


def write_result(name: str, metrics: dict, *, models: dict, settings: dict | None = None,
                 results_dir: Path = RESULTS_DIR) -> Path:
    """Write metrics with everything needed to reproduce them to eval/results/<name>.json."""
    payload = {
        'benchmark': name,
        'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'git_commit': git_commit(),
        'python': platform.python_version(),
        'device': device_name(),
        'models': models,
        'settings': settings or {},
        'metrics': metrics,
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / f'{name}.json'
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    return path


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolated percentile, as numpy computes it."""
    return float(np.percentile(np.asarray(values, dtype=np.float64), q))
