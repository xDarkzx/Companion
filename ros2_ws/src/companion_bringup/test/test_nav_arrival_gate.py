"""Integration test: agent waits for nav arrival before next step."""
import time
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
    """Launch agent + nav bridge with simulated travel."""
    places_cfg = config_path('places.yaml')
    people_cfg = config_path('people.yaml')

    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_agent',
                executable='agent_node',
                name='agent_node',
                parameters=[{
                    'places_file': places_cfg,
                    'people_file': people_cfg,
                    'speak_replies': False,
                    'wait_for_nav': True,
                    'step_delay_sec': 0.2,
                }],
            ),
            launch_ros.actions.Node(
                package='companion_body',
                executable='nav_bridge_node',
                name='nav_bridge_node',
                parameters=[{
                    'places_file': places_cfg,
                    'simulated_travel_sec': 0.4,
                    'use_nav_action': False,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestNavArrivalGate(unittest.TestCase):
    """Patrol step must not fire until nav reports arrived."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Track behavior order and timing."""
        self.node = Node('nav_gate_listener')
        self.behaviors: list[tuple[float, str]] = []
        self.command_pub = self.node.create_publisher(
            String, '/companion/voice_command', 10
        )

        def on_behavior(msg: BehaviorRequest) -> None:
            self.behaviors.append((time.time(), msg.behavior))

        self.node.create_subscription(
            BehaviorRequest,
            '/companion/behavior_request',
            on_behavior,
            10,
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_patrol_follows_go_to_after_delay(self):
        """Second step arrives noticeably after first (nav gate)."""
        self.assertTrue(wait_for_subscribers(self.command_pub))
        warm_up_dds(self.node, seconds=2.5)

        msg = String()
        msg.data = 'go to kitchen and patrol'
        self.command_pub.publish(msg)

        ok = spin_until(self.node, lambda: len(self.behaviors) >= 2, timeout_sec=15.0)
        self.assertTrue(ok, f'expected 2 behaviors, got {self.behaviors}')

        self.assertEqual(self.behaviors[0][1], 'go_to_place')
        self.assertEqual(self.behaviors[1][1], 'patrol')
        gap = self.behaviors[1][0] - self.behaviors[0][0]
        self.assertGreater(gap, 0.15, 'patrol should wait for simulated nav')
