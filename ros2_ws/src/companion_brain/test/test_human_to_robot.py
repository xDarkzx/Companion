"""MOAT empathy mapping — full affect vocabulary contract."""
from companion_brain.human_to_robot import robot_response
import pytest


@pytest.mark.parametrize(
    ('human', 'confidence', 'expected_emotion', 'min_intensity'),
    [
        ('happy', 0.9, 'happy', 0.8),
        ('sad', 0.9, 'love', 0.85),
        ('upset', 0.8, 'sad', 0.7),
        ('neutral', 0.7, 'neutral', 0.5),
        ('unknown', 0.6, 'neutral', 0.5),
    ],
)
def test_empathy_mapping(human, confidence, expected_emotion, min_intensity):
    """Human affect must map to the documented caring robot response."""
    emotion, intensity = robot_response(human, confidence)
    assert emotion == expected_emotion
    assert intensity >= min_intensity


@pytest.mark.parametrize('confidence', [0.0, 0.1, 0.34])
def test_low_confidence_never_overreacts(confidence):
    """Uncertain readings must not trigger strong empathy responses."""
    emotion, intensity = robot_response('sad', confidence)
    assert emotion == 'neutral'
    assert intensity <= 0.6
