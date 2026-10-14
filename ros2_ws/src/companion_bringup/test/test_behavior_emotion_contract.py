"""Integration test: every canonical behavior publishes the correct face emotion."""
import unittest

from companion_behaviors.behavior_modes import BEHAVIOR_EMOTIONS
from companion_interfaces.msg import BehaviorRequest, RobotEmotion
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import spin_until, wait_for_subscribers


@pytest.mark.launch_test
def generate_test_description():
    """Launch behavior controller in isolation."""
    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_behaviors',
                executable='behavior_controller_node',
                name='behavior_controller_node',
                parameters=[{'patrol_animation_sec': 5.0}],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestBehaviorEmotionContract(unittest.TestCase):
    """BehaviorRequest must always produce the documented RobotEmotion mapping."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Create behavior publisher and emotion listener."""
        self.node = Node('behavior_contract_listener')
        self.last_emotion: RobotEmotion | None = None
        self.node.create_subscription(
            RobotEmotion,
            '/companion/robot_emotion',
            self._on_emotion,
            10,
        )
        self.behavior_pub = self.node.create_publisher(
            BehaviorRequest, '/companion/behavior_request', 10
        )

    def _on_emotion(self, msg: RobotEmotion) -> None:
        self.last_emotion = msg

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def _publish_behavior(self, name: str, target: str = '') -> RobotEmotion:
        self.last_emotion = None
        req = BehaviorRequest()
        req.behavior = name
        req.target = target
        req.source = 'test'
        req.intensity = 0.9
        self.behavior_pub.publish(req)
        ok = spin_until(self.node, lambda: self.last_emotion is not None, timeout_sec=5.0)
        self.assertTrue(ok, f'no RobotEmotion for behavior {name!r}')
        assert self.last_emotion is not None
        return self.last_emotion

    def test_each_behavior_maps_to_contract_emotion(self):
        """Every behavior in BEHAVIOR_EMOTIONS produces the expected face mood."""
        self.assertTrue(wait_for_subscribers(self.behavior_pub))

        for behavior, expected_emotion in BEHAVIOR_EMOTIONS.items():
            if behavior == 'patrol':
                continue  # patrol initial emotion tested; animation is timer-driven
            msg = self._publish_behavior(
                behavior,
                target='kitchen' if behavior == 'go_to_place' else '',
            )
            self.assertEqual(
                msg.emotion,
                expected_emotion,
                f'behavior {behavior!r} should show {expected_emotion!r}',
            )
            self.assertAlmostEqual(msg.intensity, 0.9, places=2)
            self.assertEqual(msg.source, 'test')

    def test_patrol_starts_with_neutral(self):
        """Patrol behavior must begin with neutral before animation cycles."""
        self.assertTrue(wait_for_subscribers(self.behavior_pub))
        msg = self._publish_behavior('patrol')
        self.assertEqual(msg.emotion, BEHAVIOR_EMOTIONS['patrol'])
