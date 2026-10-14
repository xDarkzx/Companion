"""Integration test: voice command drives nav goal then patrol step."""
import os
import time
import unittest

from ament_index_python.packages import get_package_share_directory
from companion_interfaces.msg import BehaviorRequest
from geometry_msgs.msg import PoseStamped
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import wait_for_subscribers, warm_up_dds
from std_msgs.msg import String


def _config(name: str) -> str:
    share = get_package_share_directory('companion_bringup')
    return os.path.join(share, 'config', name)


@pytest.mark.launch_test
def generate_test_description():
    """Launch agent + nav bridge for a compound command."""
    places_cfg = _config('places.yaml')
    people_cfg = _config('people.yaml')

    agent_params = [{
        'places_file': places_cfg,
        'people_file': people_cfg,
        'step_delay_sec': 0.5,
        'wait_for_nav': True,
        'speak_replies': False,
    }]
    nav_params = [{
        'places_file': places_cfg,
        'simulated_travel_sec': 0.5,
        'use_nav_action': False,
        'map_frame': 'map',
    }]

    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_agent',
                executable='agent_node',
                name='agent_node',
                parameters=agent_params,
            ),
            launch_ros.actions.Node(
                package='companion_body',
                executable='nav_bridge_node',
                name='nav_bridge_node',
                parameters=nav_params,
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestStackCommand(unittest.TestCase):
    """Assert go-to then patrol flows through nav arrival."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Create listener and command publisher."""
        self.node = Node('stack_test_listener')
        self.behaviors: list[BehaviorRequest] = []
        self.goals: list[PoseStamped] = []
        self.node.create_subscription(
            BehaviorRequest,
            '/companion/behavior_request',
            lambda msg: self.behaviors.append(msg),
            10,
        )
        self.node.create_subscription(
            PoseStamped,
            '/goal_pose',
            lambda msg: self.goals.append(msg),
            10,
        )
        self.command_pub = self.node.create_publisher(
            String, '/companion/voice_command', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_kitchen_then_patrol(self):
        """Compound command publishes nav goal then patrol after arrival."""
        self.assertTrue(
            wait_for_subscribers(self.command_pub),
            'agent_node never subscribed to voice commands',
        )
        warm_up_dds(self.node, seconds=2.5)

        msg = String()
        msg.data = 'go to kitchen and patrol'
        self.command_pub.publish(msg)

        deadline = time.time() + 15.0
        while time.time() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.2)
            if len(self.behaviors) >= 2 and self.goals:
                break

        self.assertGreaterEqual(len(self.goals), 1, 'Expected Nav2 goal_pose')
        self.assertGreaterEqual(len(self.behaviors), 2, 'Expected two behavior steps')
        self.assertEqual(self.behaviors[0].behavior, 'go_to_place')
        self.assertEqual(self.behaviors[0].target, 'kitchen')
        self.assertEqual(self.behaviors[1].behavior, 'patrol')
