"""Integration test: patrol behavior cycles through configured places."""
import unittest

from companion_interfaces.msg import BehaviorRequest
from geometry_msgs.msg import PoseStamped
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import (
    assert_place_xy,
    config_path,
    require_subscribers,
    spin_until,
    warm_up_dds,
)


@pytest.mark.launch_test
def generate_test_description():
    """Launch nav bridge with patrol places and simulated travel."""
    places_cfg = config_path('places.yaml')

    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_body',
                executable='nav_bridge_node',
                name='nav_bridge_node',
                parameters=[{
                    'places_file': places_cfg,
                    'simulated_travel_sec': 0.3,
                    'use_nav_action': False,
                    'patrol_places': ['kitchen', 'bedroom'],
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestPatrolCyclesWaypoints(unittest.TestCase):
    """Patrol must publish sequential goals for configured places."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Track goal_pose publishes."""
        self.node = Node('patrol_cycle_listener')
        self.goals: list[tuple[float, float]] = []
        self.node.create_subscription(
            PoseStamped,
            '/goal_pose',
            lambda m: self.goals.append((m.pose.position.x, m.pose.position.y)),
            10,
        )
        self.behavior_pub = self.node.create_publisher(
            BehaviorRequest, '/companion/behavior_request', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_patrol_publishes_two_waypoints(self):
        """Patrol must hit kitchen then bedroom after simulated arrivals."""
        require_subscribers(self.behavior_pub, 'behavior_request')
        warm_up_dds(self.node, seconds=2.0)

        patrol = BehaviorRequest()
        patrol.behavior = 'patrol'
        patrol.source = 'test'
        self.behavior_pub.publish(patrol)

        ok = spin_until(self.node, lambda: len(self.goals) >= 2, timeout_sec=15.0)
        self.assertTrue(ok, f'expected 2 patrol goals, got {self.goals}')

        assert_place_xy('kitchen', self.goals[0][0], self.goals[0][1])
        assert_place_xy('bedroom', self.goals[1][0], self.goals[1][1])
