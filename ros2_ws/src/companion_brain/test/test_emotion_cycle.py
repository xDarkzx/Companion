"""Unit tests for the ROS-free emotion-cycling logic."""
from companion_brain.emotion_cycle import Emotion, select_emotion
import pytest


def test_cycles_through_sequence_in_order():
    sequence = ['neutral', 'happy', 'sad']
    assert select_emotion(0, sequence).name == 'neutral'
    assert select_emotion(1, sequence).name == 'happy'
    assert select_emotion(2, sequence).name == 'sad'


def test_wraps_around_at_end_of_sequence():
    sequence = ['neutral', 'happy']
    assert select_emotion(2, sequence).name == 'neutral'
    assert select_emotion(3, sequence).name == 'happy'


def test_applies_intensity():
    result = select_emotion(0, ['happy'], intensity=0.5)
    assert isinstance(result, Emotion)
    assert result.intensity == 0.5


def test_empty_sequence_raises():
    with pytest.raises(ValueError):
        select_emotion(0, [])


def test_out_of_range_intensity_raises():
    with pytest.raises(ValueError):
        select_emotion(0, ['happy'], intensity=1.5)
