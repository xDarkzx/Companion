"""Integration test: follow + person detection publishes /goal_pose."""
import unittest

from companion_interfaces.msg import BehaviorRequest, Detection, DetectionBatch
from geometry_msgs.msg import PoseStamped
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import (
    config_path,
    expected_follow_standoff_xy,
    require_subscribers,
    spin_until,
    warm_up_dds,
)


@pytest.mark.launch_test
def generate_test_description():
    """Launch nav bridge with sim travel off and follow anchor."""
    places_cfg = config_path('places.yaml')

    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_body',
                executable='nav_bridge_node',
                name='nav_bridge_node',
                parameters=[{
                    'places_file': places_cfg,
                    'simulated_travel_sec': 0.0,
                    'use_nav_action': False,
                    'follow_anchor_place': 'kitchen',
                    'follow_standoff_m': 0.5,
                    'follow_rate_hz': 5.0,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestFollowPublishesGoal(unittest.TestCase):
    """Person detection during follow must publish a Nav2 goal."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Track goals and publish follow + detections."""
        self.node = Node('follow_goal_listener')
        self.goals: list[PoseStamped] = []
        self.node.create_subscription(
            PoseStamped, '/goal_pose', lambda m: self.goals.append(m), 10
        )
        self.behavior_pub = self.node.create_publisher(
            BehaviorRequest, '/companion/behavior_request', 10
        )
        self.detection_pub = self.node.create_publisher(
            DetectionBatch, '/companion/detections', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_person_detection_triggers_kitchen_standoff_goal(self):
        """Follow + person must publish kitchen-offset goal (3.2+0.5*cos(1.57))."""
        require_subscribers(self.behavior_pub, 'behavior_request')
        require_subscribers(self.detection_pub, 'detections')
        warm_up_dds(self.node, seconds=2.0)

        follow = BehaviorRequest()
        follow.behavior = 'follow'
        follow.source = 'test'
        self.behavior_pub.publish(follow)

        batch = DetectionBatch()
        det = Detection()
        det.label = 'person'
        det.confidence = 0.9
        det.source = 'test'
        batch.detections.append(det)
        self.detection_pub.publish(batch)

        ok = spin_until(self.node, lambda: len(self.goals) >= 1, timeout_sec=10.0)
        self.assertTrue(ok, 'expected /goal_pose during follow with person')

        goal = self.goals[0]
        self.assertEqual(goal.header.frame_id, 'map')
        exp_x, exp_y = expected_follow_standoff_xy('kitchen', 0.5)
        self.assertAlmostEqual(goal.pose.position.x, exp_x, places=2)
        self.assertAlmostEqual(goal.pose.position.y, exp_y, places=2)

    def test_follow_without_person_publishes_no_goal(self):
        """Follow alone must not fake-navigate without a person detection."""
        require_subscribers(self.behavior_pub, 'behavior_request')
        warm_up_dds(self.node, seconds=2.0)

        follow = BehaviorRequest()
        follow.behavior = 'follow'
        follow.source = 'test'
        self.behavior_pub.publish(follow)

        spin_until(self.node, lambda: False, timeout_sec=3.0)
        self.assertEqual(
            len(self.goals),
            0,
            'follow must not publish /goal_pose without person detection',
        )
