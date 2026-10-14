"""Integration test: HumanEmotion flows through empathy to RobotEmotion."""
import unittest

from companion_interfaces.msg import HumanEmotion, RobotEmotion
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import spin_until, wait_for_subscribers, warm_up_dds


@pytest.mark.launch_test
def generate_test_description():
    """Launch empathy node only."""
    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_brain',
                executable='empathy_node',
                name='empathy_node',
                parameters=[{'min_confidence': 0.3}],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestEmpathyFlow(unittest.TestCase):
    """Publish sad HumanEmotion; expect caring RobotEmotion."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Create publisher and listener."""
        self.node = Node('empathy_test')
        self.received: list[RobotEmotion] = []
        self.node.create_subscription(
            RobotEmotion,
            '/companion/robot_emotion',
            lambda msg: self.received.append(msg),
            10,
        )
        self.human_pub = self.node.create_publisher(
            HumanEmotion, '/companion/human_emotion', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_sad_human_yields_love(self):
        """Sad human affect triggers a caring robot response."""
        self.assertTrue(
            wait_for_subscribers(self.human_pub),
            'empathy_node never subscribed to human_emotion',
        )
        warm_up_dds(self.node, seconds=2.0)

        msg = HumanEmotion()
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.emotion = 'sad'
        msg.confidence = 0.9
        msg.source = 'test'
        self.human_pub.publish(msg)

        ok = spin_until(self.node, lambda: len(self.received) >= 1, timeout_sec=10.0)
        self.assertTrue(ok, 'empathy_node never published RobotEmotion')
        self.assertEqual(self.received[0].emotion, 'love')
        self.assertEqual(self.received[0].source, 'empathy')
        self.assertAlmostEqual(self.received[0].intensity, 0.9, places=2)
