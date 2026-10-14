"""Integration test: unknown places must not emit Nav2 goals."""
import unittest

from companion_interfaces.msg import BehaviorRequest
from geometry_msgs.msg import PoseStamped
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import config_path, spin_until, wait_for_subscribers, warm_up_dds
from std_msgs.msg import String


@pytest.mark.launch_test
def generate_test_description():
    """Launch agent + nav bridge."""
    places_cfg = config_path('places.yaml')

    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_agent',
                executable='agent_node',
                name='agent_node',
                parameters=[{
                    'places_file': places_cfg,
                    'people_file': config_path('people.yaml'),
                    'speak_replies': False,
                }],
            ),
            launch_ros.actions.Node(
                package='companion_body',
                executable='nav_bridge_node',
                name='nav_bridge_node',
                parameters=[{
                    'places_file': places_cfg,
                    'use_nav_action': False,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestUnknownPlaceRejected(unittest.TestCase):
    """Commands to unknown places must fail parsing — no nav goal."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Listen for goals and behaviors."""
        self.node = Node('unknown_place_listener')
        self.goals: list[PoseStamped] = []
        self.behaviors: list[BehaviorRequest] = []
        self.node.create_subscription(
            PoseStamped, '/goal_pose', lambda m: self.goals.append(m), 10
        )
        self.node.create_subscription(
            BehaviorRequest,
            '/companion/behavior_request',
            lambda m: self.behaviors.append(m),
            10,
        )
        self.command_pub = self.node.create_publisher(
            String, '/companion/voice_command', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_garage_not_in_places_yaml(self):
        """Unknown place must not produce goal_pose or behavior steps."""
        self.assertTrue(wait_for_subscribers(self.command_pub))
        warm_up_dds(self.node, seconds=2.0)

        cmd = String()
        cmd.data = 'go to the garage'
        self.command_pub.publish(cmd)

        spin_until(self.node, lambda: False, timeout_sec=3.0)

        self.assertEqual(len(self.goals), 0, 'must not navigate to unknown place')
        self.assertEqual(len(self.behaviors), 0, 'must not emit behavior for bad parse')
