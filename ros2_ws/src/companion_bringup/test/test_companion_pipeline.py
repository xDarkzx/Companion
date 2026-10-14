"""Integration test: full voice → agent → behavior → nav → face pipeline."""
import math
import unittest

from companion_interfaces.msg import AgentState, BehaviorRequest, RobotEmotion
from geometry_msgs.msg import PoseStamped
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import (
    assert_pose_near,
    config_path,
    spin_until,
    wait_for_subscribers,
    warm_up_dds,
)
from std_msgs.msg import String

KITCHEN_X = 3.2
KITCHEN_Y = 1.1
KITCHEN_YAW = 1.57


@pytest.mark.launch_test
def generate_test_description():
    """Launch agent, behavior controller, and nav bridge together."""
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
                    'step_delay_sec': 0.3,
                    'wait_for_nav': True,
                    'speak_replies': False,
                    'session_max_turns': 10,
                }],
            ),
            launch_ros.actions.Node(
                package='companion_behaviors',
                executable='behavior_controller_node',
                name='behavior_controller_node',
                parameters=[{
                    'patrol_emotions': ['neutral', 'happy'],
                    'patrol_animation_sec': 0.5,
                }],
            ),
            launch_ros.actions.Node(
                package='companion_body',
                executable='nav_bridge_node',
                name='nav_bridge_node',
                parameters=[{
                    'places_file': places_cfg,
                    'simulated_travel_sec': 0.35,
                    'use_nav_action': False,
                    'map_frame': 'map',
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestCompanionPipeline(unittest.TestCase):
    """End-to-end checks for the core Companion command pipeline."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Wire listeners for all critical topics."""
        self.node = Node('pipeline_listener')
        self.behaviors: list[BehaviorRequest] = []
        self.goals: list[PoseStamped] = []
        self.nav_status: list[str] = []
        self.agent_states: list[str] = []
        self.emotions: list[RobotEmotion] = []

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
        self.node.create_subscription(
            String,
            '/companion/nav_status',
            lambda msg: self.nav_status.append(msg.data),
            10,
        )
        self.node.create_subscription(
            AgentState,
            '/companion/agent_state',
            lambda msg: self.agent_states.append(msg.state),
            10,
        )
        self.node.create_subscription(
            RobotEmotion,
            '/companion/robot_emotion',
            lambda msg: self.emotions.append(msg),
            10,
        )
        self.command_pub = self.node.create_publisher(
            String, '/companion/voice_command', 10
        )
        self.behavior_pub = self.node.create_publisher(
            BehaviorRequest, '/companion/behavior_request', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_voice_command_drives_nav_behaviors_and_face(self):
        """Compound command must produce correct nav, steps, and emotions."""
        self.assertTrue(
            wait_for_subscribers(self.command_pub),
            'agent_node never subscribed to voice commands',
        )
        self.assertTrue(
            wait_for_subscribers(self.behavior_pub),
            'behavior_controller never subscribed to behavior_request',
        )
        warm_up_dds(self.node, seconds=2.5)

        cmd = String()
        cmd.data = 'go to kitchen and patrol'
        self.command_pub.publish(cmd)

        ok = spin_until(
            self.node,
            lambda: (
                len(self.behaviors) >= 2
                and len(self.goals) >= 1
                and 'arrived' in self.nav_status
            ),
            timeout_sec=18.0,
        )
        self.assertTrue(
            ok,
            f'timeout: behaviors={len(self.behaviors)} goals={len(self.goals)} '
            f'nav={self.nav_status}',
        )

        self.assertEqual(self.behaviors[0].behavior, 'go_to_place')
        self.assertEqual(self.behaviors[0].target, 'kitchen')
        self.assertEqual(self.behaviors[0].source, 'voice')
        self.assertEqual(self.behaviors[1].behavior, 'patrol')

        if self.goals:
            goal = self.goals[0]
            self.assertEqual(goal.header.frame_id, 'map')
            assert_pose_near(goal.pose.position.x, goal.pose.position.y, KITCHEN_X, KITCHEN_Y)
            quat = goal.pose.orientation
            yaw = math.atan2(2.0 * quat.w * quat.z, 1.0 - 2.0 * quat.z * quat.z)
            self.assertAlmostEqual(yaw, KITCHEN_YAW, places=2)

        self.assertIn('arrived', self.nav_status)
        self.assertIn('listening', self.agent_states)
        self.assertIn('acting', self.agent_states)

        ok = spin_until(
            self.node,
            lambda: any(
                e.emotion in {'neutral', 'happy', 'surprise'}
                for e in self.emotions
            ),
            timeout_sec=4.0,
        )
        face_emotions = [e.emotion for e in self.emotions]
        self.assertTrue(
            ok,
            f'expected face emotions from behavior controller, got {face_emotions}',
        )
        self.assertIn('happy', face_emotions, 'go_to_place should publish happy')
        self.assertTrue(
            any(e in face_emotions for e in {'neutral', 'happy'}),
            f'expected patrol mood cycle, got {face_emotions}',
        )
