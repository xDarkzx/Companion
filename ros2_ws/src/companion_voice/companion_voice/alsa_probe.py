"""Helpers for listing ALSA devices on Linux (Pi voice hardware)."""
from __future__ import annotations

import subprocess


def list_capture_devices() -> list[str]:
    """Return ALSA capture device lines from arecord -l."""
    return _run_lines(['arecord', '-l'])


def list_playback_devices() -> list[str]:
    """Return ALSA playback device lines from aplay -l."""
    return _run_lines(['aplay', '-l'])


def _run_lines(cmd: list[str]) -> list[str]:
    """Run a command and return non-empty stdout lines."""
    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
