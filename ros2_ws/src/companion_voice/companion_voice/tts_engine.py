"""Route TTS requests to phrase clips, Piper, espeak, or log-only output."""
from __future__ import annotations

from companion_voice.phrase_bank import phrase_assets_dir, phrases_ready
from companion_voice.phrase_player import describe_phrases, speak_phrases
from companion_voice.piper_player import _speak_espeak, _speak_piper
from companion_voice.tts_emotion import profile_for_emotion
from companion_voice.tts_paths import discover_piper_binary, discover_piper_model
from companion_voice.tts_sanitize import sanitize_for_tts


def resolve_tts_mode(
    mode: str,
    piper_model: str = '',
    phrase_dir: str = '',
    **_kwargs,
) -> str:
    """Pick the best available engine; phrase clips win in auto mode."""
    cleaned = mode.strip().lower()
    if cleaned not in {'', 'auto'}:
        return cleaned

    folder = phrase_assets_dir(phrase_dir)
    if phrases_ready(folder):
        return 'phrases'

    model = discover_piper_model(piper_model)
    if model and discover_piper_binary():
        return 'piper'

    import shutil

    if shutil.which('espeak-ng') or shutil.which('espeak'):
        return 'espeak'
    return 'log'


def speak(
    text: str,
    mode: str,
    piper_model: str,
    output_device: str,
    emotion: str = 'neutral',
    phrase_dir: str = '',
    **_kwargs,
) -> str:
    """Speak text with the configured engine."""
    cleaned = sanitize_for_tts(text)
    if not cleaned:
        return 'empty'

    resolved = resolve_tts_mode(mode, piper_model, phrase_dir=phrase_dir)
    if resolved == 'phrases':
        return speak_phrases(cleaned, output_device, emotion, phrase_dir)
    if resolved == 'piper':
        model_path = discover_piper_model(piper_model)
        profile = profile_for_emotion(emotion)
        return _speak_piper(cleaned, model_path, output_device, profile)
    if resolved == 'espeak':
        from companion_voice.robot_voice_gen import speak_robot_espeak

        if speak_robot_espeak(cleaned, output_device):
            return 'robot_espeak'
        return _speak_espeak(cleaned, output_device)
    return 'logged'


def describe_tts(phrase_dir: str = '') -> str:
    """Human-readable summary of the active TTS backend."""
    folder = phrase_assets_dir(phrase_dir)
    if phrases_ready(folder):
        return f'phrases ({describe_phrases(phrase_dir)})'
    model = discover_piper_model()
    if model:
        return f'piper ({model})'
    return 'log/espeak'
