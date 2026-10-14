"""Follow + patrol motion: detection-driven goals and waypoint cycles."""
from __future__ import annotations

from typing import Callable

from companion_body.body_behaviors import motion_status_for
from companion_body.follow_goal import (
    person_visible,
    standoff_ahead_pose,
    standoff_from_place,
)
from companion_body.goal_pose_builder import place_to_pose
from companion_body.nav_status import FOLLOWING, IDLE, NAVIGATING
from companion_body.patrol_cycle import PatrolCycle
from companion_interfaces.msg import DetectionBatch
from companion_memory.places_store import PlacePose
from geometry_msgs.msg import PoseStamped


class MotionController:
    """Manage follow and patrol without growing nav_bridge_node."""

    def __init__(
        self,
        *,
        map_frame: str,
        places: dict[str, PlacePose],
        standoff_m: float,
        follow_min_confidence: float,
        follow_anchor: str,
        patrol_names: list[str],
        now_stamp: Callable,
        publish_nav_status,
        publish_body_status,
        send_nav_goal,
        cancel_nav,
        cancel_timers,
    ) -> None:
        """Wire callbacks supplied by NavBridgeNode."""
        self._map_frame = map_frame
        self._places = places
        self._standoff_m = standoff_m
        self._follow_min_confidence = follow_min_confidence
        self._follow_anchor = follow_anchor.strip().lower()
        self._now_stamp = now_stamp
        self._publish_nav_status = publish_nav_status
        self._publish_body_status = publish_body_status
        self._send_nav_goal = send_nav_goal
        self._cancel_nav = cancel_nav
        self._cancel_timers = cancel_timers
        self._patrol = PatrolCycle(patrol_names, places)
        self._follow_active = False
        self._patrol_active = False
        self._latest_detections: list = []

    @property
    def follow_active(self) -> bool:
        """Return True while follow mode is engaged."""
        return self._follow_active

    @property
    def patrol_active(self) -> bool:
        """Return True while patrol motion is cycling."""
        return self._patrol_active

    def stop_all(self) -> None:
        """Cancel follow and patrol motion."""
        self._follow_active = False
        self._patrol_active = False
        self._cancel_timers()
        self._cancel_nav()

    def start_follow(self) -> None:
        """Enter Nav2 follow mode (detection-driven goals)."""
        self._patrol_active = False
        self._follow_active = True
        self._cancel_nav()
        self._publish_nav_status(FOLLOWING)
        self._publish_body_status(motion_status_for('follow'))
        self._publish_follow_goal_if_person()

    def start_patrol(self) -> None:
        """Begin cycling patrol waypoints."""
        self._follow_active = False
        if not self._patrol.active:
            self._publish_body_status('motion:patrol:unconfigured')
            self._publish_nav_status(IDLE)
            return
        self._patrol_active = True
        self._publish_body_status(f'motion:patrol:{self._patrol.current_name()}')
        self._dispatch_patrol_goal()

    def acknowledge_motion(self, behavior: str) -> None:
        """Publish status for explore/play without Nav2 wiring yet."""
        self._follow_active = False
        self._patrol_active = False
        self._cancel_timers()
        status = motion_status_for(behavior)
        self._publish_nav_status(IDLE)
        self._publish_body_status(status or f'motion:{behavior}')

    def on_detections(self, batch: DetectionBatch) -> None:
        """Cache detections for follow goal updates."""
        self._latest_detections = list(batch.detections)
        if self._follow_active:
            self._publish_follow_goal_if_person()

    def on_follow_tick(self) -> None:
        """Periodic follow refresh while person is visible."""
        if self._follow_active:
            self._publish_follow_goal_if_person()

    def on_patrol_arrived(self) -> None:
        """Advance patrol after Nav2 reports arrival."""
        if not self._patrol_active:
            return
        place = self._patrol.advance()
        if place is None:
            self._patrol_active = False
            self._publish_nav_status(IDLE)
            return
        self._publish_body_status(f'motion:patrol:{self._patrol.current_name()}')
        self._dispatch_patrol_goal()

    def _publish_follow_goal_if_person(self) -> None:
        if not person_visible(self._latest_detections, self._follow_min_confidence):
            return
        pose = self._build_follow_pose()
        if pose is None:
            return
        self._send_nav_goal(pose)

    def _build_follow_pose(self) -> PoseStamped | None:
        stamp = self._now_stamp()
        anchor = self._places.get(self._follow_anchor)
        if anchor is not None:
            return standoff_from_place(anchor, self._map_frame, stamp, self._standoff_m)
        return standoff_ahead_pose(self._map_frame, stamp, self._standoff_m)

    def _dispatch_patrol_goal(self) -> None:
        place = self._patrol.current()
        if place is None:
            return
        stamp = self._now_stamp()
        pose = place_to_pose(place, self._map_frame, stamp)
        self._publish_nav_status(NAVIGATING)
        self._send_nav_goal(pose)
