"""Integration test: follow behavior drives nav + body motion status."""
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
    """Launch nav bridge only for follow motion contract."""
    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_body',
                executable='nav_bridge_node',
                name='nav_bridge_node',
                parameters=[{
                    'places_file': '',
                    'simulated_travel_sec': 0.0,
                    'use_nav_action': False,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestFollowMotionStatus(unittest.TestCase):
    """Follow behavior must publish following nav status and motion body status."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Track nav and body status strings."""
        self.node = Node('follow_motion_listener')
        self.nav_status: list[str] = []
        self.body_status: list[str] = []
        self.node.create_subscription(
            String, '/companion/nav_status', lambda m: self.nav_status.append(m.data), 10
        )
        self.node.create_subscription(
            String, '/companion/body_status', lambda m: self.body_status.append(m.data), 10
        )
        self.behavior_pub = self.node.create_publisher(
            BehaviorRequest, '/companion/behavior_request', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_follow_publishes_following_and_motion_status(self):
        """Follow request must activate follow nav + body motion contract."""
        self.assertTrue(wait_for_subscribers(self.behavior_pub))
        warm_up_dds(self.node, seconds=2.0)

        req = BehaviorRequest()
        req.behavior = 'follow'
        req.source = 'test'
        req.intensity = 0.8
        self.behavior_pub.publish(req)

        ok = spin_until(
            self.node,
            lambda: 'following' in self.nav_status and 'motion:follow' in self.body_status,
            timeout_sec=8.0,
        )
        self.assertTrue(
            ok,
            f'nav={self.nav_status} body={self.body_status}',
        )
