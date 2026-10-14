"""Integration test: 'where is the mug' goes agent -> FindObject -> spoken answer."""
import unittest

import launch
import launch_ros.actions
import launch_testing.actions
import numpy as np
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import config_path, spin_until, wait_for_subscribers, warm_up_dds
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import String

RGB_TOPIC = '/test/rgb'
DEPTH_TOPIC = '/test/depth'
INFO_TOPIC = '/test/camera_info'
WIDTH, HEIGHT = 640, 480


@pytest.mark.launch_test
def generate_test_description():
    """Launch the agent with the detector on its deterministic fake backend."""
    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_perception',
                executable='grounded_detector_node',
                name='grounded_detector_node',
                parameters=[{
                    'backend': 'fake',
                    'device': 'cpu',
                    'depth_mode': 'sensor',
                    'watch_labels': [''],
                    'rgb_topic': RGB_TOPIC,
                    'depth_topic': DEPTH_TOPIC,
                    'camera_info_topic': INFO_TOPIC,
                }],
            ),
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


class TestWhereIsFlow(unittest.TestCase):
    """The robot answers with distance and direction, or says it cannot see the object."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Create camera and command publishers and a TTS listener."""
        self.node = Node('where_is_tester')
        self.spoken: list[str] = []
        self.node.create_subscription(
            String, '/companion/tts_request', lambda msg: self.spoken.append(msg.data), 10)
        self.command_pub = self.node.create_publisher(String, '/companion/voice_command', 10)
        self.rgb_pub = self.node.create_publisher(Image, RGB_TOPIC, 10)
        self.depth_pub = self.node.create_publisher(Image, DEPTH_TOPIC, 10)
        self.info_pub = self.node.create_publisher(CameraInfo, INFO_TOPIC, 10)
        # Stream like a real camera so late subscriptions still get frames.
        self.camera_timer = self.node.create_timer(0.1, self.publish_camera)

    def tearDown(self):
        """Destroy the tester node."""
        self.node.destroy_node()

    def publish_camera(self) -> None:
        rgb = Image()
        rgb.height, rgb.width, rgb.encoding, rgb.step = HEIGHT, WIDTH, 'rgb8', WIDTH * 3
        rgb.data = bytes(WIDTH * HEIGHT * 3)
        depth = Image()
        depth.height, depth.width, depth.encoding, depth.step = HEIGHT, WIDTH, '16UC1', WIDTH * 2
        depth.data = np.full((HEIGHT, WIDTH), 1500, dtype='<u2').tobytes()
        info = CameraInfo()
        info.k = [500.0, 0.0, 320.0, 0.0, 500.0, 240.0, 0.0, 0.0, 1.0]
        self.rgb_pub.publish(rgb)
        self.depth_pub.publish(depth)
        self.info_pub.publish(info)

    def ask(self, text: str) -> str:
        self.spoken.clear()
        self.command_pub.publish(String(data=text))
        self.assertTrue(spin_until(self.node, lambda: bool(self.spoken), timeout_sec=10.0),
                        f'no spoken answer to {text!r}')
        return self.spoken[-1]

    def test_where_is_answers_with_distance_and_direction(self):
        """A visible mug is placed; an absent unicorn is reported as not seen."""
        self.assertTrue(wait_for_subscribers(self.command_pub), 'agent never subscribed')
        for pub in (self.rgb_pub, self.depth_pub, self.info_pub):
            self.assertTrue(wait_for_subscribers(pub), 'detector never subscribed')
        warm_up_dds(self.node, seconds=1.5)

        answer = self.ask('where is the mug')
        self.assertEqual(answer, 'The mug is about 1.5 metres straight ahead.')

        missing = self.ask('can you see a unicorn')
        self.assertEqual(missing, "I can't see a unicorn right now.")
