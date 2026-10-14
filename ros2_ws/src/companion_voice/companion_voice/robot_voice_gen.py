"""Generate cute English robot speech (profile-based TTS + optional sox)."""
from __future__ import annotations

from pathlib import Path
import tempfile

from companion_voice.robot_tts_profiles import default_profile_key
from companion_voice.robot_tts_synth import synthesize_profile_wav


def synthesize_robot_wav(text: str, output: Path, profile_key: str = '') -> None:
    """Write a mono WAV using the active or explicit TTS profile."""
    key = profile_key.strip() or default_profile_key()
    synthesize_profile_wav(text, output, key)


def speak_robot_espeak(text: str, output_device: str) -> bool:
    """Synthesize one line and play it (uses saved TTS profile)."""
    from companion_voice.wslg_audio import play_wav

    handle = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    handle.close()
    path = Path(handle.name)
    try:
        synthesize_robot_wav(text, path)
        return play_wav(path, output_device)
    except (OSError, RuntimeError):
        return False
    finally:
        path.unlink(missing_ok=True)
