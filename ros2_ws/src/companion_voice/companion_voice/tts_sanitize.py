"""Clean LLM / STT text before speech synthesis."""
from __future__ import annotations

import re


def sanitize_for_tts(text: str) -> str:
    """Strip emojis and non-ASCII chars TTS engines mispronounce."""
    cleaned = re.sub(r'[^\w\s\.,!?\'"\-:;()]', '', text)
    cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()
