"""Integration test: STOP must cancel a pending multi-step plan."""
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
    """Launch agent + nav bridge for stop-abort scenario."""
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


class TestStopAbortsPlan(unittest.TestCase):
    """Stop issued during navigation must not run the patrol step."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Track published behavior steps."""
        self.node = Node('stop_abort_listener')
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

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_stop_prevents_patrol_step(self):
        """After stop, patrol must never be published."""
        self.assertTrue(wait_for_subscribers(self.command_pub))
        warm_up_dds(self.node, seconds=2.0)

        start = String()
        start.data = 'go to kitchen and patrol'
        self.command_pub.publish(start)

        spin_until(self.node, lambda: 'go_to_place' in self.behaviors, timeout_sec=8.0)

        stop = String()
        stop.data = 'stop now'
        self.command_pub.publish(stop)

        spin_until(self.node, lambda: 'stop' in self.behaviors, timeout_sec=8.0)
        spin_until(self.node, lambda: False, timeout_sec=3.0)

        self.assertIn('go_to_place', self.behaviors)
        self.assertIn('stop', self.behaviors)
        self.assertNotIn(
            'patrol',
            self.behaviors,
            'patrol must not run after stop cancels the plan',
        )
