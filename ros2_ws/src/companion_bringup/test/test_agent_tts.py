"""Integration test: agent publishes TTS on recognized commands."""
import os
import time
import unittest

from ament_index_python.packages import get_package_share_directory
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


def _config(name: str) -> str:
    share = get_package_share_directory('companion_bringup')
    return os.path.join(share, 'config', name)


@pytest.mark.launch_test
def generate_test_description():
    """Launch agent node with speak_replies enabled."""
    places_cfg = _config('places.yaml')
    people_cfg = _config('people.yaml')

    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_agent',
                executable='agent_node',
                name='agent_node',
                parameters=[{
                    'places_file': places_cfg,
                    'people_file': people_cfg,
                    'speak_replies': True,
                    'wait_for_nav': False,
                    'step_delay_sec': 0.2,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestAgentTts(unittest.TestCase):
    """Assert agent emits spoken acknowledgments."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Create listener and publisher."""
        self.node = Node('agent_tts_listener')
        self.tts_msgs: list[String] = []
        self.node.create_subscription(
            String,
            '/companion/tts_request',
            lambda msg: self.tts_msgs.append(msg),
            10,
        )
        self.command_pub = self.node.create_publisher(
            String, '/companion/voice_command', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def _wait_for_agent(self) -> None:
        """Wait until the agent subscribes to voice commands."""
        deadline = time.time() + 10.0
        while time.time() < deadline and not self.command_pub.get_subscription_count():
            rclpy.spin_once(self.node, timeout_sec=0.2)

    def test_unknown_command_triggers_sorry_tts(self):
        """Unrecognized command asks for clarification via TTS."""
        self._wait_for_agent()
        msg = String()
        msg.data = 'fly to the moon'
        self.command_pub.publish(msg)

        deadline = time.time() + 10.0
        while time.time() < deadline and not self.tts_msgs:
            rclpy.spin_once(self.node, timeout_sec=0.2)

        self.assertGreaterEqual(len(self.tts_msgs), 1)
        self.assertIn('understand', self.tts_msgs[0].data.lower())

    def test_patrol_command_triggers_tts(self):
        """Known command produces a TTS acknowledgment."""
        self._wait_for_agent()
        msg = String()
        msg.data = 'patrol the home'
        self.command_pub.publish(msg)

        deadline = time.time() + 10.0
        while time.time() < deadline and not self.tts_msgs:
            rclpy.spin_once(self.node, timeout_sec=0.2)

        self.assertGreaterEqual(len(self.tts_msgs), 1)
        self.assertIn('patrol', self.tts_msgs[0].data.lower())
