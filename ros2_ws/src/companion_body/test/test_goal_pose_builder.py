"""Tests for goal pose builder."""
from builtin_interfaces.msg import Time

from companion_body.goal_pose_builder import place_to_pose, yaw_to_quaternion
from companion_memory.places_store import PlacePose


def test_yaw_to_quaternion():
    quat = yaw_to_quaternion(0.0)
    assert abs(quat.w - 1.0) < 1e-6


def test_place_to_pose():
    place = PlacePose(name='kitchen', x=3.2, y=1.1, yaw=1.57)
    stamp = Time(sec=1, nanosec=0)
    pose = place_to_pose(place, 'map', stamp)
    assert pose.header.frame_id == 'map'
    assert abs(pose.pose.position.x - 3.2) < 1e-6
    assert abs(pose.pose.position.y - 1.1) < 1e-6
