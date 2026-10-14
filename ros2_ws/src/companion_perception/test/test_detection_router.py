"""Tests for detection → behavior routing."""
from companion_interfaces.msg import Detection
from companion_perception.detection_router import behavior_hint, primary_target


def _det(label: str, confidence: float) -> Detection:
    msg = Detection()
    msg.label = label
    msg.confidence = confidence
    msg.source = 'test'
    return msg


def test_dog_hints_play():
    assert behavior_hint([_det('dog', 0.8)]) == 'play_with_dog'


def test_person_hints_follow():
    assert behavior_hint([_det('person', 0.7)]) == 'follow'


def test_primary_target_picks_best():
    assert primary_target([_det('person', 0.5), _det('dog', 0.9)]) == 'dog'
