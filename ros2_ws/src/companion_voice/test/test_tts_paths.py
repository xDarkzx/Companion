"""Tests for Piper ONNX model discovery."""
from pathlib import Path

from companion_voice.tts_paths import discover_piper_model, tts_search_dirs


def test_discover_explicit_model(tmp_path: Path, monkeypatch):
    """Configured model path wins over search dirs."""
    model = tmp_path / 'custom.onnx'
    model.write_bytes(b'onnx')
    monkeypatch.setenv('COMPANION_TTS_DIR', str(tmp_path / 'missing'))
    assert discover_piper_model(str(model)) == str(model)


def test_discover_from_user_tts_dir(tmp_path: Path, monkeypatch):
    """Scan ~/companion/tts style folders for ONNX files."""
    user_tts = tmp_path / 'companion' / 'tts'
    user_tts.mkdir(parents=True)
    voice = user_tts / 'en_US-lessac-medium.onnx'
    voice.write_bytes(b'onnx')
    monkeypatch.setenv('COMPANION_TTS_DIR', str(user_tts))
    assert discover_piper_model('') == str(voice)


def test_tts_search_dirs_respects_env(monkeypatch, tmp_path: Path):
    """COMPANION_TTS_DIR is first in the search order."""
    custom = tmp_path / 'my_tts'
    custom.mkdir()
    monkeypatch.setenv('COMPANION_TTS_DIR', str(custom))
    dirs = tts_search_dirs()
    assert dirs[0] == custom
