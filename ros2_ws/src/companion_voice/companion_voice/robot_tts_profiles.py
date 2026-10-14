"""Named TTS profiles for previewing and batch-generating robot phrase clips."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RobotTtsProfile:
    """One robot voice recipe: engine knobs + optional sox polish."""

    key: str
    label: str
    backend: str  # espeak | piper
    espeak_voice: str = 'en-us'
    espeak_speed: int = 168
    espeak_pitch: int = 78
    fx: str = 'none'
    piper_model: str = 'en_US-amy-medium'


ROBOT_TTS_PROFILES: tuple[RobotTtsProfile, ...] = (
    RobotTtsProfile(
        key='piper_amy_chibi',
        label='Piper Amy — local neural + chibi polish',
        backend='piper',
        piper_model='en_US-amy-medium',
        fx='chibi',
    ),
    RobotTtsProfile(
        key='piper_lessac_robot',
        label='Piper Lessac — local neural + robot polish',
        backend='piper',
        piper_model='en_US-lessac-medium',
        fx='robot',
    ),
    RobotTtsProfile(
        key='espeak_chibi',
        label='espeak-ng — offline fallback (chibi)',
        backend='espeak',
        espeak_speed=168,
        espeak_pitch=78,
        fx='chibi',
    ),
    RobotTtsProfile(
        key='espeak_robot',
        label='espeak-ng — offline fallback (deeper robot)',
        backend='espeak',
        espeak_speed=145,
        espeak_pitch=42,
        fx='robot',
    ),
)

DEFAULT_PROFILE_KEY = 'espeak_chibi'

PREVIEW_LINES: tuple[str, ...] = (
    'Hello! I am Companion!',
    'Yay! So happy!',
    'On my way!',
)


def list_profile_keys() -> list[str]:
    """Return profile keys in display order."""
    return [profile.key for profile in ROBOT_TTS_PROFILES]


def get_profile(key: str) -> RobotTtsProfile:
    """Look up a profile by key."""
    cleaned = key.strip().lower()
    for profile in ROBOT_TTS_PROFILES:
        if profile.key == cleaned:
            return profile
    raise KeyError(f'unknown TTS profile: {key}')


def default_profile_key() -> str:
    """Resolve saved profile or fall back to the recommended default."""
    from pathlib import Path
    import os

    env = os.environ.get('COMPANION_TTS_PROFILE', '').strip()
    if env:
        return env

    root = os.environ.get('COMPANION_ROOT', '').strip()
    if root:
        marker = Path(root) / 'assets' / 'phrases' / 'active_profile.txt'
        if marker.is_file():
            saved = marker.read_text(encoding='utf-8').strip()
            if saved:
                return saved

    return DEFAULT_PROFILE_KEY
