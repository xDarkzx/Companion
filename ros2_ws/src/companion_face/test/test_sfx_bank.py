"""Unit tests for SFX asset resolution."""
from pathlib import Path

from companion_face.sfx_bank import list_loaded_sfx, resolve_sfx_path


def test_resolve_missing_returns_none(tmp_path: Path):
    """Missing assets must fall back to synth in SfxPlayer."""
    assert resolve_sfx_path(tmp_path, 'happy') is None


def test_resolve_wav_file(tmp_path: Path):
    """WAV files in assets dir must be discovered by key."""
    (tmp_path / 'happy.wav').write_bytes(b'RIFF')
    assert resolve_sfx_path(tmp_path, 'happy') == tmp_path / 'happy.wav'
    assert 'happy' in list_loaded_sfx(tmp_path)
