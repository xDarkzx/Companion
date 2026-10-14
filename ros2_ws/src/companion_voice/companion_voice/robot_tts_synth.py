"""Synthesize one robot phrase clip from a named TTS profile."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from companion_voice.robot_tts_fx import apply_fx
from companion_voice.robot_tts_profiles import get_profile, RobotTtsProfile
from companion_voice.tts_paths import discover_piper_binary


def synthesize_profile_wav(text: str, output: Path, profile_key: str) -> None:
    """Render text to WAV using the given profile."""
    profile = get_profile(profile_key)
    cleaned = text.strip()
    if not cleaned:
        raise ValueError('empty text')

    with tempfile.TemporaryDirectory(prefix='companion_tts_') as tmp:
        work = Path(tmp)
        raw = work / 'raw.wav'
        _render_backend(cleaned, raw, profile)
        apply_fx(raw, output, profile.fx)


def _render_backend(text: str, output: Path, profile: RobotTtsProfile) -> None:
    if profile.backend == 'espeak':
        _render_espeak(text, output, profile)
        return
    if profile.backend == 'piper':
        _render_piper(text, output, profile)
        return
    raise RuntimeError(f'unsupported backend: {profile.backend}')


def _render_espeak(text: str, output: Path, profile: RobotTtsProfile) -> None:
    espeak = shutil.which('espeak-ng') or shutil.which('espeak')
    if espeak is None:
        raise RuntimeError('espeak-ng not installed')

    subprocess.run(
        [
            espeak,
            '-v', profile.espeak_voice,
            '-s', str(profile.espeak_speed),
            '-p', str(profile.espeak_pitch),
            '-a', '200',
            '-w', str(output),
            text,
        ],
        check=True,
        capture_output=True,
    )


def _render_piper(text: str, output: Path, profile: RobotTtsProfile) -> None:
    piper_bin = discover_piper_binary()
    model = _resolve_piper_model(profile.piper_model)
    if not piper_bin or not model:
        raise RuntimeError(
            'piper not installed — run: bash scripts/desktop_install_piper.sh'
        )

    subprocess.run(
        [
            piper_bin,
            '--model', str(model),
            '--output_file', str(output),
        ],
        input=text.encode('utf-8'),
        check=True,
        capture_output=True,
    )


def _resolve_piper_model(model_name: str) -> Path | None:
    root = os.environ.get('COMPANION_ROOT', '').strip()
    candidates: list[Path] = []
    if root:
        candidates.append(
            Path(root) / 'models' / 'piper' / model_name / f'{model_name}.onnx'
        )
    candidates.append(
        Path.home() / 'companion' / 'piper' / model_name / f'{model_name}.onnx'
    )
    for path in candidates:
        if path.is_file():
            return path
    return None
