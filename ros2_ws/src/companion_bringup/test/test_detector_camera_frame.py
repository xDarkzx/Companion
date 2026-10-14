"""Integration test: detector_node reacts to published camera frames."""
import time
import unittest

from companion_interfaces.msg import DetectionBatch
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import wait_for_subscribers, warm_up_dds
from sensor_msgs.msg import Image


@pytest.mark.launch_test
def generate_test_description():
    """Launch detector with camera subscription enabled."""
    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_perception',
                executable='detector_node',
                name='detector_node',
                parameters=[{
                    'model_path': '',
                    'publish_rate_hz': 2.0,
                    'use_camera': True,
                    'source_label': 'stub',
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestDetectorCameraFrame(unittest.TestCase):
    """Camera frames must change idle → camera_ready in stub mode."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Subscribe to detection batches and publish fake RGB frames."""
        self.node = Node('detector_camera_listener')
        self.labels: list[str] = []
        self.node.create_subscription(
            DetectionBatch,
            '/companion/detections',
            lambda msg: self.labels.append(msg.detections[0].label),
            10,
        )
        self.image_pub = self.node.create_publisher(
            Image, '/ascamera/camera_publisher/rgb0/image', 10
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_camera_frame_switches_from_idle_to_ready(self):
        """Without YOLO, receiving RGB must publish camera_ready."""
        self.assertTrue(
            wait_for_subscribers(self.image_pub),
            'detector_node never subscribed to RGB topic',
        )
        warm_up_dds(self.node, seconds=2.5)

        frame = Image()
        frame.height = 2
        frame.width = 2
        frame.encoding = 'rgb8'
        frame.step = 6
        frame.data = bytes([0] * 12)

        end = time.time() + 10.0
        ok = False
        while time.time() < end:
            self.image_pub.publish(frame)
            rclpy.spin_once(self.node, timeout_sec=0.2)
            if 'camera_ready' in self.labels:
                ok = True
                break

        self.assertTrue(
            ok,
            f'expected camera_ready after frame, got labels={self.labels}',
        )
