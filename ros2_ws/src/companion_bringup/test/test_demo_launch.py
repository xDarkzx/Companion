"""Integration test: the demo launch publishes RobotEmotion the graph can see."""
import time
import unittest

from companion_interfaces.msg import RobotEmotion
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import warm_up_dds


@pytest.mark.launch_test
def generate_test_description():
    """Launch the brain and face nodes for the test."""
    brain = launch_ros.actions.Node(
        package='companion_brain',
        executable='heartbeat_node',
        name='heartbeat_node',
        parameters=[{'publish_rate_hz': 5.0}],
    )
    face = launch_ros.actions.Node(
        package='companion_face',
        executable='face_stub_node',
        name='face_stub_node',
    )
    return (
        launch.LaunchDescription([brain, face, launch_testing.actions.ReadyToTest()]),
        {},
    )


class TestEmotionFlows(unittest.TestCase):
    """Assert a RobotEmotion message actually flows on the topic."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Create a listener node that records received emotions."""
        self.node = Node('test_listener')
        self.received = []
        self.node.create_subscription(
            RobotEmotion,
            '/companion/robot_emotion',
            lambda msg: self.received.append(msg),
            10,
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_robot_emotion_is_published(self):
        """Assert heartbeat publishes valid RobotEmotion with required fields."""
        warm_up_dds(self.node, seconds=2.0)
        deadline = time.time() + 10.0
        while time.time() < deadline and not self.received:
            rclpy.spin_once(self.node, timeout_sec=0.5)
        self.assertGreater(
            len(self.received), 0, 'No RobotEmotion received within 10s'
        )
        msg = self.received[0]
        self.assertEqual(msg.source, 'brain')
        self.assertGreaterEqual(msg.intensity, 0.0)
        self.assertLessEqual(msg.intensity, 1.0)
        self.assertGreater(msg.header.stamp.sec + msg.header.stamp.nanosec, 0)
        expected = {'neutral', 'happy', 'sad', 'angry', 'love'}
        self.assertIn(msg.emotion, expected)
