"""Find objects named in plain words: a FindObject service plus a watch list for follow hints."""
from __future__ import annotations

import sys

from companion_interfaces.msg import DetectionBatch
from companion_interfaces.srv import FindObject
from companion_perception.annotate import draw_boxes
from companion_perception.detection_router import behavior_hint
from companion_perception.image_bridge import depth_image_to_array, image_to_rgb, rgb_to_image
from companion_perception.mentorpi_camera import (
    CAMERA_INFO_TOPIC,
    DEPTH_IMAGE_TOPIC,
    RGB_IMAGE_TOPIC,
)
from companion_perception.ros_convert import (
    intrinsics_from_camera_info,
    search_outcome,
    to_detection2d_array,
    to_detection3d_array,
    to_watch_batch,
)
from companion_vision.depth import DepthLoadError, load_depth
from companion_vision.detector import DetectorLoadError, load_detector, normalize_queries
from companion_vision.pipeline import Finder
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image
from std_msgs.msg import Header, String
from vision_msgs.msg import Detection3DArray

FIND_SERVICE = '/companion/find_object'
OBJECTS_TOPIC = '/companion/objects'
ANNOTATED_TOPIC = '/companion/perception/annotated'
DETECTION_TOPIC = '/companion/detections'
HINT_TOPIC = '/companion/detection_hint'
QUEUE_DEPTH = 10
WAITING_LABEL = 'waiting_for_camera'


def resolve_device(requested: str) -> str:
    """Use the requested device; 'auto' picks CUDA when torch can see a GPU."""
    if requested != 'auto':
        return requested
    try:
        import torch
    except ImportError:
        return 'cpu'
    return 'cuda' if torch.cuda.is_available() else 'cpu'


class GroundedDetectorNode(Node):
    """Keep only the latest camera frame and run detection on demand or for the watch list."""

    def __init__(self) -> None:
        """Declare parameters, load models (failing loudly), and wire topics and service."""
        super().__init__('grounded_detector_node')
        self.declare_parameter('backend', 'owlv2')
        self.declare_parameter('device', 'auto')
        self.declare_parameter('depth_mode', 'sensor')
        self.declare_parameter('score_threshold', 0.2)
        self.declare_parameter('watch_labels', ['person', 'dog'])
        self.declare_parameter('watch_rate_hz', 2.0)
        self.declare_parameter('rgb_topic', RGB_IMAGE_TOPIC)
        self.declare_parameter('depth_topic', DEPTH_IMAGE_TOPIC)
        self.declare_parameter('camera_info_topic', CAMERA_INFO_TOPIC)

        backend = str(self.get_parameter('backend').value)
        device = resolve_device(str(self.get_parameter('device').value))
        depth_mode = str(self.get_parameter('depth_mode').value)
        threshold = float(self.get_parameter('score_threshold').value)
        watch = [str(label) for label in self.get_parameter('watch_labels').value if label]
        self._watch = normalize_queries(watch) if watch else ()

        detector = load_detector(backend, device=device, score_threshold=threshold)
        depth = load_depth(depth_mode, device=device)
        self._finder = Finder(detector, depth, intrinsics=None)
        self._source = detector.name
        self._rgb = None
        self._depth = None
        self._header = Header()
        self._warned_no_intrinsics = False

        self.create_subscription(
            Image, str(self.get_parameter('rgb_topic').value), self._on_rgb, QUEUE_DEPTH)
        self.create_subscription(
            Image, str(self.get_parameter('depth_topic').value), self._on_depth, QUEUE_DEPTH)
        self.create_subscription(
            CameraInfo, str(self.get_parameter('camera_info_topic').value), self._on_info,
            QUEUE_DEPTH)
        self.create_service(FindObject, FIND_SERVICE, self._on_find)
        self._objects_pub = self.create_publisher(Detection3DArray, OBJECTS_TOPIC, QUEUE_DEPTH)
        self._annotated_pub = self.create_publisher(Image, ANNOTATED_TOPIC, QUEUE_DEPTH)
        self._batch_pub = self.create_publisher(DetectionBatch, DETECTION_TOPIC, QUEUE_DEPTH)
        self._hint_pub = self.create_publisher(String, HINT_TOPIC, QUEUE_DEPTH)

        rate = float(self.get_parameter('watch_rate_hz').value)
        if self._watch and rate > 0.0:
            self._watch_timer = self.create_timer(1.0 / rate, self._on_watch)
        self.get_logger().info(
            f'Finding objects with {backend} on {device}, depth={depth_mode}, '
            f'watching {list(self._watch) or "nothing"}; service {FIND_SERVICE}'
        )

    def _on_rgb(self, msg: Image) -> None:
        """Keep only the newest frame, so a slow model never builds a backlog."""
        rgb = image_to_rgb(msg)
        if rgb is not None:
            self._rgb = rgb
            self._header = msg.header

    def _on_depth(self, msg: Image) -> None:
        """Keep only the newest depth frame."""
        self._depth = depth_image_to_array(msg)

    def _on_info(self, msg: CameraInfo) -> None:
        """Take the camera model from CameraInfo."""
        self._finder.set_intrinsics(intrinsics_from_camera_info(msg))

    def _locate(self, queries):
        """Run the pipeline on the latest frame and publish the 3D results and annotated view."""
        located = self._finder.find(self._rgb, queries, sensor_depth=self._depth)
        self._objects_pub.publish(to_detection3d_array(located, self._header))
        annotated = rgb_to_image(draw_boxes(self._rgb, located))
        annotated.header = self._header
        self._annotated_pub.publish(annotated)
        if located and all(item.xyz is None for item in located) and (
                not self._warned_no_intrinsics):
            self.get_logger().warn('Objects found but none placed in 3D: check depth/CameraInfo')
            self._warned_no_intrinsics = True
        return located

    def _on_find(self, request: FindObject.Request, response: FindObject.Response):
        """Answer one query from the latest frame, always with a reason."""
        response.found = False
        try:
            queries = normalize_queries([request.query])
        except ValueError:
            response.reason = FindObject.Response.REASON_BAD_QUERY
            return response
        if self._rgb is None:
            response.reason = FindObject.Response.REASON_NO_FRAME
            return response
        located = self._locate(queries)
        response.found, response.reason = search_outcome(located)
        response.detections = to_detection2d_array(located, self._header)
        response.objects = to_detection3d_array(located, self._header)
        self.get_logger().info(f'find {queries[0]!r}: {response.reason} ({len(located)} match)')
        return response

    def _on_watch(self) -> None:
        """Publish watch-list detections and a follow/play hint for the existing consumers."""
        if self._rgb is None:
            batch = to_watch_batch([], self._header, self._source)
            batch.detections[0].label = WAITING_LABEL
            self._batch_pub.publish(batch)
            return
        batch = to_watch_batch(self._locate(self._watch), self._header, self._source)
        self._batch_pub.publish(batch)
        hint = behavior_hint(list(batch.detections))
        if hint:
            self._hint_pub.publish(String(data=hint))


def main(args=None) -> None:
    """Spin with clean shutdown; exit non-zero if a model cannot be loaded."""
    rclpy.init(args=args)
    node = None
    exit_code = 0
    try:
        node = GroundedDetectorNode()
        rclpy.spin(node)
    except (DetectorLoadError, DepthLoadError) as exc:
        rclpy.logging.get_logger('grounded_detector_node').fatal(f'{type(exc).__name__}: {exc}')
        exit_code = 1
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    if exit_code:
        sys.exit(exit_code)


if __name__ == '__main__':
    main()
