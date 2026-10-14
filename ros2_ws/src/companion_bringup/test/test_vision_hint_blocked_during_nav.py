"""Integration test: vision hints must not interrupt an active navigation plan."""
import unittest

from companion_interfaces.msg import BehaviorRequest
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
    """Launch agent + nav bridge with vision reactivity enabled."""
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
                    'react_to_vision': True,
                    'vision_hint_cooldown_sec': 0.5,
                    'wait_for_nav': True,
                    'speak_replies': False,
                    'step_delay_sec': 0.2,
                }],
            ),
            launch_ros.actions.Node(
                package='companion_body',
                executable='nav_bridge_node',
                name='nav_bridge_node',
                parameters=[{
                    'places_file': places_cfg,
                    'simulated_travel_sec': 2.0,
                    'use_nav_action': False,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestVisionHintBlockedDuringNav(unittest.TestCase):
    """Follow hints during navigation must not publish extra behaviors."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Track behavior requests."""
        self.node = Node('vision_block_listener')
        self.behaviors: list[str] = []
        self.node.create_subscription(
            BehaviorRequest,
            '/companion/behavior_request',
            lambda msg: self.behaviors.append(msg.behavior),
            10,
        )
        self.command_pub = self.node.create_publisher(
            String, '/companion/voice_command', 10
        )
        self.hint_pub = self.node.create_publisher(
            String, '/companion/detection_hint', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_follow_hint_ignored_while_navigating(self):
        """Vision must not inject follow during an active go-to plan."""
        self.assertTrue(wait_for_subscribers(self.command_pub))
        self.assertTrue(wait_for_subscribers(self.hint_pub))
        warm_up_dds(self.node, seconds=2.0)

        cmd = String()
        cmd.data = 'go to kitchen and patrol'
        self.command_pub.publish(cmd)

        spin_until(
            self.node,
            lambda: 'go_to_place' in self.behaviors,
            timeout_sec=8.0,
        )

        hint = String()
        hint.data = 'follow'
        self.hint_pub.publish(hint)

        spin_until(self.node, lambda: False, timeout_sec=2.0)

        self.assertNotIn(
            'follow',
            self.behaviors,
            'follow hint must not fire while agent waits for nav',
        )
