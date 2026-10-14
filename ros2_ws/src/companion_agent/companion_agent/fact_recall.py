"""Turn fact recall questions into spoken replies."""
from __future__ import annotations

from companion_memory.fact_store import FactStore
from companion_voice.reply_catalog import phrase_text, recall_reply

_QUESTION_PREFIXES = (
    'what is ',
    "what's ",
    'what was ',
    'tell me ',
    'do you remember ',
    'do you know ',
    'recall ',
)


def looks_like_recall_query(text: str) -> bool:
    """Return True when the user is asking to retrieve a stored fact."""
    cleaned = text.strip().lower()
    if not cleaned:
        return False
    if cleaned.endswith('?'):
        return True
    return any(cleaned.startswith(prefix) for prefix in _QUESTION_PREFIXES)


def format_recall_reply(fact: str) -> str:
    """Format a stored fact as a short spoken answer."""
    return recall_reply(fact)


def try_recall_reply(text: str, fact_store: FactStore | None) -> str | None:
    """Return a spoken reply when a stored fact matches the question."""
    if fact_store is None or not looks_like_recall_query(text):
        return None
    facts = fact_store.search(text, limit=1)
    if not facts:
        return phrase_text('no_memory')
    return format_recall_reply(facts[0])
