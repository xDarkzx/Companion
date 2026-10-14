"""Integration test: remember command stores facts and RAG retrieves them."""
import os
import tempfile
import time
import unittest

from ament_index_python.packages import get_package_share_directory
from companion_interfaces.msg import AgentState
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
    """Launch agent with a temp fact database enabled."""
    places_cfg = _config('places.yaml')
    people_cfg = _config('people.yaml')
    fact_db = os.path.join(tempfile.gettempdir(), 'companion_test_facts.db')

    agent_params = [{
        'places_file': places_cfg,
        'people_file': people_cfg,
        'fact_db_path': fact_db,
        'max_stored_facts': 50,
        'speak_replies': True,
        'speak_welcome': False,
        'wait_for_nav': False,
        'step_delay_sec': 0.2,
    }]

    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_agent',
                executable='agent_node',
                name='agent_node',
                parameters=agent_params,
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestRememberFactFlow(unittest.TestCase):
    """Assert remember → retrieve path through agent_state and TTS."""

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
        self.node = Node('remember_fact_listener')
        self.tts_msgs: list[String] = []
        self.states: list[AgentState] = []
        self.node.create_subscription(
            String,
            '/companion/tts_request',
            lambda msg: self.tts_msgs.append(msg),
            10,
        )
        self.node.create_subscription(
            AgentState,
            '/companion/agent_state',
            lambda msg: self.states.append(msg),
            10,
        )
        self.command_pub = self.node.create_publisher(
            String, '/companion/voice_command', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_remember_then_rag_retrieves_fact(self):
        """Stored facts must surface in agent RAG state on a later query."""
        self.assertTrue(
            wait_for_subscribers(self.command_pub),
            'agent_node never subscribed to voice commands',
        )
        warm_up_dds(self.node, seconds=2.0)

        remember = String()
        remember.data = 'remember that the garage code is 4455'
        self.command_pub.publish(remember)

        deadline = time.time() + 10.0
        while time.time() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.2)
            if self.tts_msgs and any(
                s.rag_used and s.memory_count >= 1 for s in self.states
            ):
                break

        self.assertGreaterEqual(len(self.tts_msgs), 1)
        self.assertIn('remember', self.tts_msgs[0].data.lower())

        self.tts_msgs.clear()
        self.states.clear()

        query = String()
        query.data = 'what is the garage code'
        self.command_pub.publish(query)

        deadline = time.time() + 10.0
        rag_hit = None
        while time.time() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.2)
            for state in self.states:
                if state.rag_used and 'fact:' in state.status_text:
                    rag_hit = state
                    break
            if rag_hit is not None:
                break

        self.assertIsNotNone(rag_hit, 'Expected RAG hit with stored fact')
        self.assertGreaterEqual(rag_hit.memory_count, 1)
        self.assertIn('garage', rag_hit.status_text.lower())

        deadline = time.time() + 10.0
        while time.time() < deadline and not self.tts_msgs:
            rclpy.spin_once(self.node, timeout_sec=0.2)

        self.assertGreaterEqual(len(self.tts_msgs), 1)
        self.assertIn('4455', self.tts_msgs[0].data)
