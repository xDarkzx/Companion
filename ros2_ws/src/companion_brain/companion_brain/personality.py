"""Voice / interaction events -> robot emotion (needy, playful, cute)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from companion_brain.emotion_cycle import Emotion


class VoiceEvent(str, Enum):
    """What the robot heard or inferred from the human (stub until real STT)."""

    WAKE = 'wake'
    PRAISE = 'praise'
    SCOLD = 'scold'
    IGNORE = 'ignore'
    SILENCE = 'silence'
    COMMAND_OK = 'command_ok'
    COMMAND_FAIL = 'command_fail'
    PLAY = 'play'


@dataclass(frozen=True)
class PersonalityState:
    """Short memory for needy behaviour (bounded, no unbounded growth)."""

    lonely_ticks: int = 0
    last_emotion: str = 'neutral'


def react_to_voice(event: VoiceEvent, state: PersonalityState) -> tuple[Emotion, PersonalityState]:
    """Pick robot emotion + updated state from a voice/interaction event."""
    lonely = state.lonely_ticks
    if event == VoiceEvent.WAKE:
        return Emotion('surprise', 0.9), PersonalityState(0, 'surprise')
    if event == VoiceEvent.PRAISE:
        return Emotion('happy', 1.0), PersonalityState(0, 'happy')
    if event == VoiceEvent.PLAY:
        return Emotion('happy', 0.85), PersonalityState(0, 'happy')
    if event == VoiceEvent.SCOLD:
        return Emotion('sad', 0.9), PersonalityState(lonely + 1, 'sad')
    if event == VoiceEvent.COMMAND_OK:
        return Emotion('love', 0.75), PersonalityState(0, 'love')
    if event == VoiceEvent.COMMAND_FAIL:
        return Emotion('cry', 0.7), PersonalityState(lonely, 'cry')
    if event in (VoiceEvent.IGNORE, VoiceEvent.SILENCE):
        lonely += 1
        if lonely >= 4:
            return Emotion('cry', 0.8), PersonalityState(lonely, 'cry')
        if lonely >= 2:
            return Emotion('sad', 0.75), PersonalityState(lonely, 'sad')
        return Emotion('love', 0.6), PersonalityState(lonely, 'love')
    return Emotion('neutral', 0.5), state
