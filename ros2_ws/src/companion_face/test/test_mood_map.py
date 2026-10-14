"""Tests for RobotEmotion -> ASCII mood mapping."""
from companion_face.mood_map import mood_for_emotion, ROS_TO_MOOD


def test_all_ros_emotions_mapped():
    for key in ROS_TO_MOOD:
        assert mood_for_emotion(key) == ROS_TO_MOOD[key]


def test_unknown_falls_back_neutral():
    assert mood_for_emotion('unknown_mood') == 'neutral'
