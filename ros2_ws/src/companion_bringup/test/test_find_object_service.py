"""Integration test: grounded_detector_node answers FindObject from camera, depth and K."""
import time
import unittest

from companion_interfaces.srv import FindObject
import launch
import launch_ros.actions
import launch_testing.actions
import numpy as np
import pytest
import rclpy
from rclpy.node import Node
from ros_test_helpers import wait_for_subscribers, warm_up_dds
from sensor_msgs.msg import CameraInfo, Image

RGB_TOPIC = '/test/rgb'
DEPTH_TOPIC = '/test/depth'
INFO_TOPIC = '/test/camera_info'
WIDTH, HEIGHT = 640, 480


@pytest.mark.launch_test
def generate_test_description():
    """Launch the detector with the deterministic fake backend and sensor depth."""
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
                    'watch_labels': ['person'],
                    'rgb_topic': RGB_TOPIC,
                    'depth_topic': DEPTH_TOPIC,
                    'camera_info_topic': INFO_TOPIC,
                }],
            ),
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


def rgb_frame() -> Image:
    msg = Image()
    msg.header.frame_id = 'camera_color_optical_frame'
    msg.height, msg.width, msg.encoding, msg.step = HEIGHT, WIDTH, 'rgb8', WIDTH * 3
    msg.data = bytes(WIDTH * HEIGHT * 3)
    return msg


def depth_frame(millimetres: int) -> Image:
    msg = Image()
    msg.height, msg.width, msg.encoding, msg.step = HEIGHT, WIDTH, '16UC1', WIDTH * 2
    msg.data = np.full((HEIGHT, WIDTH), millimetres, dtype='<u2').tobytes()
    return msg


def camera_info() -> CameraInfo:
    msg = CameraInfo()
    msg.width, msg.height = WIDTH, HEIGHT
    msg.k = [500.0, 0.0, 320.0, 0.0, 500.0, 240.0, 0.0, 0.0, 1.0]
    return msg


class TestFindObjectService(unittest.TestCase):
    """The service must answer from the latest frame and explain every miss."""

    @classmethod
    def setUpClass(cls):
        """Initialise rclpy once for the test case."""
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        """Shut down rclpy after the test case."""
        rclpy.shutdown()

    def setUp(self):
        """Create camera publishers and the FindObject client."""
        self.node = Node('find_object_tester')
        self.rgb_pub = self.node.create_publisher(Image, RGB_TOPIC, 10)
        self.depth_pub = self.node.create_publisher(Image, DEPTH_TOPIC, 10)
        self.info_pub = self.node.create_publisher(CameraInfo, INFO_TOPIC, 10)
        self.client = self.node.create_client(FindObject, '/companion/find_object')

    def tearDown(self):
        """Destroy the tester node."""
        self.node.destroy_node()

    def call(self, query: str, timeout: float = 5.0):
        request = FindObject.Request()
        request.query = query
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=timeout)
        self.assertTrue(future.done(), f'no FindObject answer for {query!r}')
        return future.result()

    def publish_camera(self, frames: int = 1) -> None:
        for _ in range(frames):
            self.rgb_pub.publish(rgb_frame())
            self.depth_pub.publish(depth_frame(1500))
            self.info_pub.publish(camera_info())
        warm_up_dds(self.node, seconds=1.0)

    def test_find_object_flow(self):
        """No frame, then a found object in 3D, a bad query, a miss, and a frame burst."""
        self.assertTrue(self.client.wait_for_service(timeout_sec=15.0), 'service never appeared')

        before = self.call('mug')
        self.assertFalse(before.found)
        self.assertEqual(before.reason, FindObject.Response.REASON_NO_FRAME)

        for pub in (self.rgb_pub, self.depth_pub, self.info_pub):
            self.assertTrue(wait_for_subscribers(pub), 'node never subscribed to the camera')
        self.publish_camera()

        mug = self.call('mug')
        self.assertTrue(mug.found)
        self.assertEqual(mug.reason, FindObject.Response.REASON_OK)
        position = mug.objects.detections[0].bbox.center.position
        self.assertAlmostEqual(position.z, 1.5, places=2)
        self.assertAlmostEqual(position.x, 0.0, places=2)
        self.assertEqual(mug.objects.header.frame_id, 'camera_color_optical_frame')

        blank = self.call('   ')
        self.assertFalse(blank.found)
        self.assertEqual(blank.reason, FindObject.Response.REASON_BAD_QUERY)

        miss = self.call('unicorn')
        self.assertFalse(miss.found)
        self.assertEqual(miss.reason, FindObject.Response.REASON_NO_MATCH)

        self.publish_camera(frames=50)
        start = time.time()
        after_burst = self.call('mug', timeout=2.0)
        self.assertLess(time.time() - start, 2.0)
        self.assertTrue(after_burst.found)
