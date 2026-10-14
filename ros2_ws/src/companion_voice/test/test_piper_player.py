"""Tests for TTS engine routing."""
from pathlib import Path

from companion_voice.tts_engine import resolve_tts_mode, speak


def test_speak_empty():
    assert speak('', 'log', '', '') == 'empty'


def test_speak_log_mode():
    assert speak('hello', 'log', '', '') == 'logged'


def test_resolve_auto_without_engines(monkeypatch):
    """Auto mode falls back to espeak when no phrases or Piper exist."""
    monkeypatch.setattr('companion_voice.tts_engine.phrases_ready', lambda _folder: False)
    monkeypatch.setattr(
        'companion_voice.tts_engine.discover_piper_model', lambda explicit='': ''
    )
    monkeypatch.setattr(
        'companion_voice.tts_engine.discover_piper_binary', lambda: ''
    )
    monkeypatch.setattr('shutil.which', lambda _name: '/usr/bin/espeak-ng')
    assert resolve_tts_mode('auto') == 'espeak'


def test_resolve_auto_prefers_phrases(monkeypatch, tmp_path):
    """Auto mode uses phrase clips when enough WAVs exist."""
    (tmp_path / 'hello.wav').write_bytes(b'wav')
    (tmp_path / 'stop.wav').write_bytes(b'wav')
    (tmp_path / 'okay.wav').write_bytes(b'wav')
    (tmp_path / 'yes.wav').write_bytes(b'wav')
    (tmp_path / 'no.wav').write_bytes(b'wav')
    monkeypatch.setattr(
        'companion_voice.tts_engine.phrase_assets_dir',
        lambda explicit='': Path(tmp_path),
    )
    assert resolve_tts_mode('auto', phrase_dir=str(tmp_path)) == 'phrases'


def test_resolve_auto_prefers_piper_when_no_phrases(monkeypatch, tmp_path):
    """Auto mode uses Piper when phrase clips are missing."""
    model = tmp_path / 'voice.onnx'
    model.write_bytes(b'onnx')

    monkeypatch.setattr('companion_voice.tts_engine.phrases_ready', lambda _folder: False)
    monkeypatch.setattr(
        'companion_voice.tts_engine.discover_piper_model',
        lambda explicit='': str(model),
    )
    monkeypatch.setattr(
        'companion_voice.tts_engine.discover_piper_binary',
        lambda: '/usr/bin/piper',
    )
    assert resolve_tts_mode('auto', str(model)) == 'piper'
