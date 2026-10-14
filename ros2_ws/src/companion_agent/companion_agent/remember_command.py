"""Parse 'remember that ...' voice commands into fact text."""
from __future__ import annotations

import re

_REMEMBER_PATTERNS = (
    re.compile(r'^remember\s+that\s+(.+)$', re.IGNORECASE),
    re.compile(r'^remember\s+(.+)$', re.IGNORECASE),
    re.compile(r"^don'?t\s+forget\s+that\s+(.+)$", re.IGNORECASE),
    re.compile(r'^please\s+remember\s+(?:that\s+)?(.+)$', re.IGNORECASE),
)


def parse_remember_fact(text: str) -> str | None:
    """Return fact text when input is a remember command, else None."""
    cleaned = ' '.join(text.strip().split())
    if not cleaned:
        return None
    for pattern in _REMEMBER_PATTERNS:
        match = pattern.match(cleaned)
        if match:
            fact = match.group(1).strip()
            return fact or None
    return None
