"""Build Nav2 goal poses from named places."""
from __future__ import annotations

import math

from companion_memory.places_store import PlacePose
from geometry_msgs.msg import PoseStamped, Quaternion


def yaw_to_quaternion(yaw: float) -> Quaternion:
    """Convert planar yaw radians to a geometry_msgs quaternion."""
    quat = Quaternion()
    quat.z = math.sin(yaw / 2.0)
    quat.w = math.cos(yaw / 2.0)
    return quat


def place_to_pose(
    place: PlacePose,
    frame_id: str,
    stamp,
) -> PoseStamped:
    """Create a map-frame PoseStamped for Nav2."""
    pose = PoseStamped()
    pose.header.stamp = stamp
    pose.header.frame_id = frame_id
    pose.pose.position.x = place.x
    pose.pose.position.y = place.y
    pose.pose.orientation = yaw_to_quaternion(place.yaw)
    return pose
