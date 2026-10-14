"""Integration test: STOP during navigation must cancel nav and publish idle."""
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
    """Launch agent + nav bridge for nav-cancel scenario."""
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
                    'simulated_travel_sec': 4.0,
                    'use_nav_action': False,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestNavStopCancels(unittest.TestCase):
    """Stop must abort in-flight navigation before simulated arrival."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Track nav status and behavior steps."""
        self.node = Node('nav_stop_listener')
        self.nav_status: list[str] = []
        self.behaviors: list[str] = []
        self.node.create_subscription(
            String,
            '/companion/nav_status',
            lambda msg: self.nav_status.append(msg.data),
            10,
        )
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

    def test_stop_cancels_navigating_before_arrival(self):
        """Nav must return idle on stop and must not report arrived."""
        self.assertTrue(wait_for_subscribers(self.command_pub))
        warm_up_dds(self.node, seconds=2.0)

        go = String()
        go.data = 'go to kitchen'
        self.command_pub.publish(go)

        spin_until(
            self.node,
            lambda: 'navigating' in self.nav_status,
            timeout_sec=8.0,
        )

        stop = String()
        stop.data = 'stop now'
        self.command_pub.publish(stop)

        spin_until(
            self.node,
            lambda: 'stop' in self.behaviors and 'idle' in self.nav_status,
            timeout_sec=8.0,
        )
        spin_until(self.node, lambda: False, timeout_sec=2.0)

        self.assertIn('go_to_place', self.behaviors)
        self.assertIn('stop', self.behaviors)
        self.assertIn('navigating', self.nav_status)
        self.assertIn('idle', self.nav_status)
        self.assertNotIn(
            'arrived',
            self.nav_status,
            'stop must cancel nav before simulated arrival',
        )
