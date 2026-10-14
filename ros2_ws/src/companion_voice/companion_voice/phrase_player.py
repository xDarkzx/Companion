"""Play pre-recorded English robot phrase clips (desk-pet style)."""
from __future__ import annotations

from pathlib import Path

from companion_voice.phrase_bank import (
    clip_path,
    match_phrase_key,
    phrase_assets_dir,
    phrases_ready,
    recall_tail_text,
)
from companion_voice.piper_player import _speak_espeak
from companion_voice.robot_voice_gen import speak_robot_espeak


def speak_phrases(
    text: str,
    output_device: str,
    emotion: str = 'neutral',
    assets_dir: str = '',
) -> str:
    """Play the closest phrase clip; fall back to pitched espeak."""
    folder = phrase_assets_dir(assets_dir)
    tail = recall_tail_text(text)
    if tail is not None:
        return _speak_recall(folder, output_device, tail)

    key = match_phrase_key(text, emotion)
    path = clip_path(folder, key)
    if path is not None:
        from companion_voice.wslg_audio import play_wav

        if play_wav(path, output_device):
            return f'phrase:{key}'
    if speak_robot_espeak(text, output_device):
        return 'robot_espeak'
    return _speak_espeak(text, output_device)


def _speak_recall(folder: Path, output_device: str, fact_tail: str) -> str:
    """Play recall lead clip, then TTS for the dynamic fact."""
    from companion_voice.wslg_audio import play_wav

    key = 'recall_lead'
    path = clip_path(folder, key)
    if path is not None:
        play_wav(path, output_device)
    if speak_robot_espeak(fact_tail, output_device):
        return 'phrase:recall+tts'
    return _speak_espeak(fact_tail, output_device)


def describe_phrases(assets_dir: str = '') -> str:
    """Summary string for logging."""
    folder = phrase_assets_dir(assets_dir)
    if not phrases_ready(folder):
        return 'none'
    from companion_voice.phrase_bank import list_loaded_phrases

    loaded = list_loaded_phrases(folder)
    return f'{len(loaded)} clips @ {folder.name}'
