"""Optional local LLM replies via Ollama (natural speech instead of templates)."""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

DEFAULT_BASE = 'http://127.0.0.1:11434'
DEFAULT_MODEL = 'llama3.2'
TIMEOUT_SEC = 45.0
MAX_HISTORY = 10


def _sanitize_reply(text: str) -> str:
    """Strip chars that TTS engines mispronounce."""
    cleaned = re.sub(r'[^\w\s\.,!?\'"\-:;()]', '', text)
    cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def generate_reply(
    user_text: str,
    context: str = '',
    base_url: str = DEFAULT_BASE,
    model: str = DEFAULT_MODEL,
    history: tuple[tuple[str, str], ...] = (),
) -> str | None:
    """Ask Ollama for a short in-character reply; None if unavailable."""
    cleaned = user_text.strip()
    if not cleaned:
        return None

    system = (
        'You are Companion, a small English-speaking robot desk pet. '
        'Reply in ONE short sentence only — plain spoken English, no markdown. '
        'Sound helpful and friendly, not silly or meme-like. '
        'Examples: "Hello!", "On my way to the kitchen.", '
        '"Got it. I\'ll remember that.", "Sorry, I didn\'t understand that." '
        'Never claim you moved unless the user asked for navigation.'
    )
    if context.strip():
        system = f'{system}\n\nContext: {context.strip()}'

    messages = [{'role': 'system', 'content': system}]
    for role, text in history[-MAX_HISTORY:]:
        if text.strip():
            messages.append({'role': role, 'content': text.strip()})
    messages.append({'role': 'user', 'content': cleaned})

    body = json.dumps({
        'model': model,
        'messages': messages,
        'stream': False,
        'options': {
            'temperature': 0.85,
            'num_predict': 120,
            'num_ctx': 2048,
        },
    }).encode('utf-8')

    url = base_url.rstrip('/') + '/api/chat'
    request = urllib.request.Request(
        url,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SEC) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None

    message = payload.get('message') or {}
    reply = _sanitize_reply(str(message.get('content', '')).strip())
    return reply or None


def is_available(base_url: str = DEFAULT_BASE) -> bool:
    """Return True when Ollama responds on the configured host."""
    url = base_url.rstrip('/') + '/api/tags'
    try:
        with urllib.request.urlopen(url, timeout=2.0) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
