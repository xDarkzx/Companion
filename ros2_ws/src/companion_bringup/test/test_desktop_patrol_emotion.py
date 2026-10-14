"""Integration test: desktop-style patrol drives face emotions via behaviors."""
import os
import time
import unittest

from ament_index_python.packages import get_package_share_directory
from companion_behaviors.behavior_modes import BEHAVIOR_EMOTIONS
from companion_interfaces.msg import BehaviorRequest, RobotEmotion
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import wait_for_subscribers, warm_up_dds
from std_msgs.msg import String


def _share_config(name: str) -> str:
    share = get_package_share_directory('companion_bringup')
    return os.path.join(share, 'config', name)


@pytest.mark.launch_test
def generate_test_description():
    """Launch desktop stack subset: agent + behaviors (no pygame face)."""
    desktop_cfg = _share_config('desktop_dev.yaml')
    places_cfg = _share_config('places.yaml')
    people_cfg = _share_config('people.yaml')

    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_agent',
                executable='agent_node',
                name='agent_node',
                parameters=[
                    desktop_cfg,
                    {
                        'places_file': places_cfg,
                        'people_file': people_cfg,
                        'welcome_message': '',
                        'wait_for_nav': False,
                        'speak_replies': False,
                    },
                ],
            ),
            launch_ros.actions.Node(
                package='companion_behaviors',
                executable='behavior_controller_node',
                name='behavior_controller_node',
                parameters=[desktop_cfg],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestDesktopPatrolEmotion(unittest.TestCase):
    """Patrol command from the desktop prototype must publish patrol emotions."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Create listeners and command publisher."""
        self.node = Node('desktop_patrol_listener')
        self.emotions: list[RobotEmotion] = []
        self.behaviors: list[BehaviorRequest] = []
        self.node.create_subscription(
            RobotEmotion,
            '/companion/robot_emotion',
            lambda msg: self.emotions.append(msg),
            10,
        )
        self.node.create_subscription(
            BehaviorRequest,
            '/companion/behavior_request',
            lambda msg: self.behaviors.append(msg),
            10,
        )
        self.command_pub = self.node.create_publisher(
            String, '/companion/voice_command', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_patrol_publishes_behavior_and_emotion(self):
        """Desktop patrol phrase must trigger patrol behavior and face emotion."""
        self.assertTrue(
            wait_for_subscribers(self.command_pub),
            'agent_node never subscribed to voice commands',
        )
        warm_up_dds(self.node, seconds=2.0)

        msg = String()
        msg.data = 'patrol the home'
        self.command_pub.publish(msg)

        deadline = time.time() + 12.0
        while time.time() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.2)
            if self.behaviors and self.emotions:
                break

        self.assertGreaterEqual(len(self.behaviors), 1)
        self.assertEqual(self.behaviors[0].behavior, 'patrol')
        self.assertGreaterEqual(len(self.emotions), 1)
        self.assertEqual(self.emotions[0].emotion, BEHAVIOR_EMOTIONS['patrol'])
