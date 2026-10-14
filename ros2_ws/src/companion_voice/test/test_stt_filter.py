"""Tests for Whisper transcript filtering."""
from companion_voice.stt_filter import filter_transcription


def test_filter_empty():
    result = filter_transcription('')
    assert result.skipped
    assert result.reason == 'empty'


def test_filter_too_short():
    result = filter_transcription('hi')
    assert result.skipped
    assert result.reason == 'too_short'


def test_filter_accepts_normal_phrase():
    result = filter_transcription('hello companion')
    assert not result.skipped
    assert result.text == 'hello companion'
