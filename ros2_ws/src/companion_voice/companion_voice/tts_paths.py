"""Locate Piper ONNX models and binary from user or project TTS folders."""
from __future__ import annotations

import os
from pathlib import Path
import shutil

ONNX_SUFFIX = '.onnx'
PREFERRED_VOICES = (
    'en_US-lessac-medium.onnx',
    'en_US-amy-medium.onnx',
    'en_GB-alan-medium.onnx',
)


def project_root() -> Path | None:
    """Return Companion repo root when running from a checkout."""
    env = os.environ.get('COMPANION_ROOT', '').strip()
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / 'ros2_ws').is_dir() and (parent / 'scripts').is_dir():
            return parent
    return None


def tts_search_dirs() -> list[Path]:
    """Ordered folders to scan for voice models (first match wins)."""
    dirs: list[Path] = []
    env_dir = os.environ.get('COMPANION_TTS_DIR', '').strip()
    if env_dir:
        dirs.append(Path(os.path.expanduser(env_dir)))

    dirs.append(Path(os.path.expanduser('~/companion/tts')))

    root = project_root()
    if root is not None:
        dirs.append(root / 'tts')
        dirs.append(root / 'models' / 'piper')

    seen: set[str] = set()
    unique: list[Path] = []
    for directory in dirs:
        key = str(directory)
        if key in seen:
            continue
        seen.add(key)
        unique.append(directory)
    return unique


def _onnx_files(directory: Path) -> list[Path]:
    """List ONNX files under a directory tree."""
    if not directory.is_dir():
        return []
    return sorted(directory.rglob(f'*{ONNX_SUFFIX}'))


def discover_piper_model(explicit: str = '') -> str:
    """Pick the best Piper ONNX model from config or known TTS folders."""
    cleaned = explicit.strip()
    if cleaned:
        path = Path(cleaned)
        if path.is_file():
            return str(path)

    for base in tts_search_dirs():
        for name in PREFERRED_VOICES:
            direct = base / name
            if direct.is_file():
                return str(direct)
            nested = base / name.replace('.onnx', '') / name
            if nested.is_file():
                return str(nested)

    for base in tts_search_dirs():
        files = _onnx_files(base)
        if files:
            return str(files[0])
    return ''


def discover_piper_binary() -> str:
    """Find the piper CLI on PATH or in models/piper."""
    found = shutil.which('piper')
    if found:
        return found

    root = project_root()
    if root is None:
        return ''

    bundled = root / 'models' / 'piper' / 'piper' / 'piper'
    if bundled.is_file() and os.access(bundled, os.X_OK):
        return str(bundled)
    return ''
