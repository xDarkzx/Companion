"""Build Nav2 follow goals when a person is visible."""
from __future__ import annotations

import math

from companion_body.detection_targets import person_confidence
from companion_body.goal_pose_builder import place_to_pose, yaw_to_quaternion
from companion_interfaces.msg import Detection
from companion_memory.places_store import PlacePose
from geometry_msgs.msg import PoseStamped


def person_visible(detections: list[Detection], min_confidence: float) -> bool:
    """Return True when a person detection exceeds the confidence gate."""
    return person_confidence(detections, min_confidence) > 0.0


def standoff_ahead_pose(
    frame_id: str,
    stamp,
    distance_m: float,
    yaw: float = 0.0,
) -> PoseStamped:
    """Publish a goal ``distance_m`` ahead on +X (dev / sim follow stub)."""
    pose = PoseStamped()
    pose.header.stamp = stamp
    pose.header.frame_id = frame_id
    pose.pose.position.x = float(distance_m)
    pose.pose.position.y = 0.0
    pose.pose.orientation = yaw_to_quaternion(yaw)
    return pose


def standoff_from_place(
    place: PlacePose,
    frame_id: str,
    stamp,
    standoff_m: float,
) -> PoseStamped:
    """Offset a named place goal slightly along its heading for follow standoff."""
    base = place_to_pose(place, frame_id, stamp)
    yaw = place.yaw
    base.pose.position.x += math.cos(yaw) * standoff_m
    base.pose.position.y += math.sin(yaw) * standoff_m
    return base
