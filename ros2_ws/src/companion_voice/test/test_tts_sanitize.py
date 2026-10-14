"""Tests for TTS text sanitization."""
from companion_voice.tts_sanitize import sanitize_for_tts


def test_sanitize_strips_emoji():
    assert sanitize_for_tts('Hello 😀 world') == 'Hello world'


def test_sanitize_collapses_whitespace():
    assert sanitize_for_tts('Hi   there') == 'Hi there'
