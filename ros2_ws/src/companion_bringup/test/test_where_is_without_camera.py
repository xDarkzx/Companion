"""Integration test: with no perception running, the agent says so instead of hanging."""
import unittest

import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import config_path, spin_until, wait_for_subscribers
from std_msgs.msg import String


@pytest.mark.launch_test
def generate_test_description():
    """Launch only the agent: the FindObject service does not exist."""
    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_agent',
                executable='agent_node',
                name='agent_node',
                parameters=[{
                    'places_file': config_path('places.yaml'),
                    'people_file': config_path('people.yaml'),
                    'speak_replies': True,
                    'speak_welcome': False,
                    'wait_for_nav': False,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestWhereIsWithoutCamera(unittest.TestCase):
    """A find request must still get a prompt, honest answer."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Create the command publisher and a TTS listener."""
        self.node = Node('where_is_no_camera_tester')
        self.spoken: list[str] = []
        self.node.create_subscription(
            String, '/companion/tts_request', lambda msg: self.spoken.append(msg.data), 10)
        self.command_pub = self.node.create_publisher(String, '/companion/voice_command', 10)

    def tearDown(self):
        """Destroy the tester node."""
        self.node.destroy_node()

    def test_missing_perception_is_reported(self):
        """The agent answers that it cannot check the camera."""
        self.assertTrue(wait_for_subscribers(self.command_pub), 'agent never subscribed')
        self.command_pub.publish(String(data='where is the mug'))
        self.assertTrue(spin_until(self.node, lambda: bool(self.spoken), timeout_sec=10.0))
        self.assertEqual(self.spoken[-1], "I can't check my camera right now.")
