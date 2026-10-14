"""Unit tests for follow goal helpers."""
from companion_body.follow_goal import person_visible, standoff_ahead_pose
from companion_interfaces.msg import Detection


def _det(label: str, confidence: float) -> Detection:
    msg = Detection()
    msg.label = label
    msg.confidence = confidence
    msg.source = 'test'
    return msg


def test_person_visible_requires_confidence():
    assert person_visible([_det('person', 0.8)], 0.4)
    assert not person_visible([_det('person', 0.2)], 0.4)


def test_standoff_ahead_pose():
    pose = standoff_ahead_pose('map', stamp=None, distance_m=2.0)
    assert pose.header.frame_id == 'map'
    assert pose.pose.position.x == 2.0
