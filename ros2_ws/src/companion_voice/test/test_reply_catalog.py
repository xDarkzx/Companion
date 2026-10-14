"""Tests for reply catalog."""
from companion_voice.reply_catalog import (
    BOOT_GREETING_KEYS,
    catalog_phrase_dict,
    going_place_text,
    phrase_text,
    recall_reply,
)


def test_boot_keys_no_meme():
    assert 'uwu' not in BOOT_GREETING_KEYS


def test_going_kitchen():
    assert going_place_text('kitchen') == phrase_text('going_kitchen')


def test_recall_reply():
    assert recall_reply('blue') == 'I remember. blue.'


def test_catalog_has_core_commands():
    keys = catalog_phrase_dict()
    for key in ('hello', 'stop', 'patrol', 'dont_understand', 'remember_ok'):
        assert key in keys
