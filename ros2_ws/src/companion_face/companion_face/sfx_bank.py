"""Load robot SFX (beeps/boops) from WAV/OGG with synth fallback."""
from __future__ import annotations

from pathlib import Path

# Short non-speech robot sounds — see assets/sfx/README.md
SFX_FILES = {
    'blink': ('blink_FNZ3zVv.mp3', 'blink.wav', 'blink.ogg'),
    'listen': ('listen.wav', 'listen.ogg', 'select_001.ogg'),
    'think': ('think.wav', 'think.ogg', 'scroll_001.ogg'),
    'confirm': ('confirm.wav', 'confirm.ogg', 'confirmation_001.ogg'),
    'alert': ('alert.wav', 'alert.ogg', 'error_001.ogg'),
    'happy': ('happy.wav', 'happy.ogg', 'bong_001.ogg'),
    'love': ('love.wav', 'love.ogg', 'happy.wav'),
    'surprise': ('surprise.wav', 'surprise.ogg', 'pluck_001.ogg'),
    'sad': ('sad.wav', 'sad.ogg'),
    'cry': ('sad.wav', 'sad.ogg'),
    'neutral': ('neutral.wav', 'neutral.ogg'),
    'yawn': ('yawn.wav', 'yawn.ogg'),
    'wake': ('wake.wav', 'wake.ogg', 'power_up_001.ogg'),
}

EMOTION_TO_SFX = {
    'happy': 'happy',
    'love': 'love',
    'surprise': 'surprise',
    'sad': 'sad',
    'cry': 'sad',
    'sleepy': 'yawn',
    'neutral': 'neutral',
    'focused': 'think',
    'angry': 'alert',
}

AGENT_STATE_SFX: dict[str, str] = {
    'listening': 'listen',
    'retrieving': 'think',
    'thinking': 'think',
    'acting': 'confirm',
    'error': 'alert',
}


def resolve_sfx_path(assets_dir: Path, key: str) -> Path | None:
    """Return the first matching asset file for a logical SFX key."""
    names = SFX_FILES.get(key, ())
    for name in names:
        path = assets_dir / name
        if path.is_file():
            return path
    return None


def list_loaded_sfx(assets_dir: Path) -> list[str]:
    """Return keys that have at least one file on disk."""
    loaded: list[str] = []
    for key in SFX_FILES:
        if resolve_sfx_path(assets_dir, key) is not None:
            loaded.append(key)
    return loaded
