"""Unit tests for emotion-aware Piper profiles."""
from companion_voice.tts_emotion import profile_for_emotion


def test_happy_is_faster_than_sad():
    """Happy speech should use a shorter length scale than sad."""
    happy = profile_for_emotion('happy')
    sad = profile_for_emotion('sad')
    assert happy.length_scale < sad.length_scale


def test_unknown_emotion_uses_neutral():
    """Unknown moods must map to the neutral profile."""
    neutral = profile_for_emotion('neutral')
    unknown = profile_for_emotion('not_a_real_mood')
    assert unknown.length_scale == neutral.length_scale
