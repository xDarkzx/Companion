"""Agent boot greetings aligned with phrase clips."""
from __future__ import annotations

from companion_voice.reply_catalog import BOOT_GREETING_KEYS, phrase_text


def boot_greeting_text(seed: int | None = None) -> str:
    """Pick a boot greeting line from the catalog."""
    import random

    key = random.Random(seed).choice(BOOT_GREETING_KEYS)
    return phrase_text(key)
