"""Integration test: vision detection hints trigger behaviors when agent is idle."""
import unittest

from companion_interfaces.msg import BehaviorRequest
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import spin_until, wait_for_subscribers, warm_up_dds
from std_msgs.msg import String


@pytest.mark.launch_test
def generate_test_description():
    """Launch agent with vision reactivity enabled."""
    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_agent',
                executable='agent_node',
                name='agent_node',
                parameters=[{
                    'react_to_vision': True,
                    'vision_hint_cooldown_sec': 0.5,
                    'speak_replies': False,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestVisionHintTriggers(unittest.TestCase):
    """Detection hints must publish follow when agent has no active plan."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Track behavior requests from vision hints."""
        self.node = Node('vision_hint_listener')
        self.behaviors: list[BehaviorRequest] = []
        self.node.create_subscription(
            BehaviorRequest,
            '/companion/behavior_request',
            lambda msg: self.behaviors.append(msg),
            10,
        )
        self.hint_pub = self.node.create_publisher(
            String, '/companion/detection_hint', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_person_hint_publishes_follow(self):
        """A follow hint must become a behavior request with source vision."""
        self.assertTrue(
            wait_for_subscribers(self.hint_pub),
            'agent_node never subscribed to detection hints',
        )
        warm_up_dds(self.node, seconds=2.0)

        hint = String()
        hint.data = 'follow'
        self.hint_pub.publish(hint)

        ok = spin_until(
            self.node,
            lambda: any(b.behavior == 'follow' for b in self.behaviors),
            timeout_sec=8.0,
        )
        self.assertTrue(ok, f'expected follow behavior, got {self.behaviors}')
        follow = next(b for b in self.behaviors if b.behavior == 'follow')
        self.assertEqual(follow.source, 'vision')
