"""Integration test: detector_node publishes typed DetectionBatch messages."""
import unittest

from companion_interfaces.msg import DetectionBatch
import launch
import launch_ros.actions
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node

from ros_test_helpers import spin_until, warm_up_dds


@pytest.mark.launch_test
def generate_test_description():
    """Launch detector in stub mode."""
    return (
        launch.LaunchDescription([
            launch_ros.actions.Node(
                package='companion_perception',
                executable='detector_node',
                name='detector_node',
                parameters=[{
                    'model_path': '',
                    'publish_rate_hz': 2.0,
                    'use_camera': False,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestDetectorPublishesBatch(unittest.TestCase):
    """Perception must publish DetectionBatch on /companion/detections."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Subscribe to detection batches."""
        self.node = Node('detector_listener')
        self.batches: list[DetectionBatch] = []
        self.node.create_subscription(
            DetectionBatch,
            '/companion/detections',
            lambda msg: self.batches.append(msg),
            10,
        )

    def tearDown(self):
        """Destroy the listener node."""
        self.node.destroy_node()

    def test_stub_mode_publishes_idle_detection(self):
        """Without YOLO model, node must still publish a valid idle batch."""
        warm_up_dds(self.node, seconds=2.0)
        ok = spin_until(self.node, lambda: len(self.batches) >= 1, timeout_sec=8.0)
        self.assertTrue(ok, 'detector_node never published DetectionBatch')

        batch = self.batches[0]
        self.assertEqual(batch.header.frame_id, 'camera')
        self.assertGreaterEqual(len(batch.detections), 1)
        self.assertEqual(batch.detections[0].label, 'idle')
        self.assertEqual(batch.detections[0].source, 'stub')
        self.assertAlmostEqual(batch.detections[0].confidence, 1.0, places=2)
