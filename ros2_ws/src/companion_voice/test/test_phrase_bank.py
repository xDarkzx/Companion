"""Tests for robot phrase matching."""
from pathlib import Path

from companion_voice.phrase_bank import (
    match_phrase_key,
    phrases_ready,
    pick_boot_greeting_key,
    text_slug,
)


def test_match_hello():
    assert match_phrase_key('Hello there friend!') == 'hello'


def test_match_stop():
    assert match_phrase_key('Stopping now.') == 'stop'


def test_match_patrol():
    assert match_phrase_key('Starting patrol.') == 'patrol'


def test_match_emotion_fallback():
    assert match_phrase_key('...', emotion='happy') == 'happy'


def test_text_slug():
    assert text_slug('How are you?') == 'how_are_you'


def test_phrases_ready_false(tmp_path: Path):
    assert phrases_ready(tmp_path) is False


def test_boot_greeting_key():
    assert pick_boot_greeting_key(0) in {
        'hello', 'how_are_you', 'hi', 'welcome', 'here_to_help',
    }
