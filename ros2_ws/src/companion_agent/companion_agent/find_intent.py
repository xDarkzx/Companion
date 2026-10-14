"""Recognise requests to find an object: 'where is the mug', 'can you see a dog'."""
from __future__ import annotations

import re

_FIND_RE = re.compile(
    r'^(?:please\s+)?(?:can you\s+|could you\s+)?'
    r"(?:where\s+is|where's|find|see|look\s+for|do\s+you\s+see)\s+(?P<rest>.+)$",
    re.IGNORECASE,
)
_ARTICLES = frozenset({'the', 'my', 'a', 'an', 'your', 'our'})


def parse_find(text: str) -> str | None:
    """Return the object to look for, or None if the text is not a find request."""
    cleaned = ' '.join(text.strip().rstrip('?.!').split())
    match = _FIND_RE.match(cleaned)
    if match is None:
        return None
    words = match.group('rest').lower().split()
    while words and words[0] in _ARTICLES:
        words.pop(0)
    return ' '.join(words) or None
