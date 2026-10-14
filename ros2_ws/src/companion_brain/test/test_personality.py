"""Tests for voice-driven personality emotion selection."""
from companion_brain.personality import PersonalityState, react_to_voice, VoiceEvent


def test_praise_makes_happy():
    emo, st = react_to_voice(VoiceEvent.PRAISE, PersonalityState())
    assert emo.name == 'happy'
    assert emo.intensity == 1.0
    assert st.lonely_ticks == 0


def test_ignore_gets_needier():
    st = PersonalityState()
    emo1, st = react_to_voice(VoiceEvent.IGNORE, st)
    assert emo1.name == 'love'
    emo2, st = react_to_voice(VoiceEvent.IGNORE, st)
    assert emo2.name == 'sad'
    emo3, st = react_to_voice(VoiceEvent.IGNORE, st)
    assert emo3.name == 'sad'
    emo4, _ = react_to_voice(VoiceEvent.IGNORE, st)
    assert emo4.name == 'cry'


def test_wake_is_surprised():
    emo, _ = react_to_voice(VoiceEvent.WAKE, PersonalityState())
    assert emo.name == 'surprise'
