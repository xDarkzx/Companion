"""Map agent replies to pre-recorded English robot phrase clips."""
from __future__ import annotations

import re
from pathlib import Path

from companion_voice.reply_catalog import (
    BOOT_GREETING_KEYS,
    EMOTION_PHRASE_KEY,
    TEXT_RULES,
    catalog_phrase_dict,
    text_slug,
)

# Spoken text for each clip key (used when generating WAVs).
ROBOT_PHRASES: dict[str, str] = catalog_phrase_dict()


def phrase_assets_dir(explicit: str = '') -> Path:
    """Resolve phrase WAV folder (param, env, or package share)."""
    import os

    cleaned = explicit.strip()
    if cleaned:
        return Path(cleaned)

    env = os.environ.get('COMPANION_PHRASE_DIR', '').strip()
    if env:
        return Path(env)

    root = os.environ.get('COMPANION_ROOT', '').strip()
    if root:
        bundled = Path(root) / 'ros2_ws' / 'src' / 'companion_voice' / 'assets' / 'phrases'
        if bundled.is_dir():
            return bundled
        generated = Path(root) / 'assets' / 'phrases'
        if generated.is_dir():
            return generated

    try:
        from ament_index_python.packages import get_package_share_directory

        share = Path(get_package_share_directory('companion_voice')) / 'assets' / 'phrases'
        if share.is_dir():
            return share
    except Exception:  # noqa: BLE001 — optional outside ROS
        pass

    return Path('assets/phrases')


def clip_path(assets_dir: Path, key: str) -> Path | None:
    """Return the first existing WAV/OGG/MP3 for a phrase key."""
    for ext in ('.wav', '.ogg', '.mp3'):
        path = assets_dir / f'{key}{ext}'
        if path.is_file():
            return path
    return None


def phrases_ready(assets_dir: Path, minimum: int = 5) -> bool:
    """True when enough phrase clips exist to use phrase mode."""
    if not assets_dir.is_dir():
        return False
    count = sum(1 for key in ROBOT_PHRASES if clip_path(assets_dir, key) is not None)
    return count >= minimum


def list_loaded_phrases(assets_dir: Path) -> list[str]:
    """Return phrase keys that have audio on disk."""
    return [key for key in ROBOT_PHRASES if clip_path(assets_dir, key) is not None]


def pick_boot_greeting_key(seed: int | None = None) -> str:
    """Random boot clip key."""
    import random

    return random.Random(seed).choice(BOOT_GREETING_KEYS)


def match_phrase_key(text: str, emotion: str = 'neutral') -> str:
    """Pick the best pre-recorded clip for an agent reply line."""
    cleaned = text.strip()
    if not cleaned:
        return EMOTION_PHRASE_KEY.get(emotion.lower(), 'okay')

    lower = cleaned.lower()
    for pattern, key in TEXT_RULES:
        if re.search(pattern, lower):
            return key

    slug = text_slug(cleaned)
    if slug in ROBOT_PHRASES:
        return slug

    return EMOTION_PHRASE_KEY.get(emotion.lower(), 'okay')


def recall_tail_text(text: str) -> str | None:
    """Return the fact tail after 'I remember.' when present."""
    lower = text.strip().lower()
    lead = ROBOT_PHRASES.get('recall_lead', 'I remember.').lower().rstrip('.')
    if lower.startswith(lead):
        tail = text.strip()[len(lead):].strip().lstrip(':., ')
        return tail or None
    return None
