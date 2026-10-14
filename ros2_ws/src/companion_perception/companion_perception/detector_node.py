"""Publish typed DetectionBatch messages (YOLO CPU on live camera or idle stub)."""
from companion_interfaces.msg import Detection, DetectionBatch
from companion_perception.detection_router import behavior_hint
from companion_perception.image_bridge import image_to_bgr
from companion_perception.mentorpi_camera import RGB_IMAGE_TOPIC
from companion_perception.yolo_cpu import detect_in_frame, detect_labels, try_load_yolo
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

DETECTION_TOPIC = '/companion/detections'
HINT_TOPIC = '/companion/detection_hint'
QUEUE_DEPTH = 10


class DetectorNode(Node):
    """Run YOLO on RGB camera frames when configured; otherwise publish idle batches."""

    def __init__(self) -> None:
        """Wire publishers, camera subscription, and optional YOLO model."""
        super().__init__('detector_node')
        self.declare_parameter('model_path', '')
        self.declare_parameter('publish_rate_hz', 1.0)
        self.declare_parameter('frame_width', 640)
        self.declare_parameter('frame_height', 480)
        self.declare_parameter('source_label', 'stub')
        self.declare_parameter('rgb_topic', RGB_IMAGE_TOPIC)
        self.declare_parameter('use_camera', True)

        model_path = str(self.get_parameter('model_path').value)
        self._source = str(self.get_parameter('source_label').value)
        self._width = int(self.get_parameter('frame_width').value)
        self._height = int(self.get_parameter('frame_height').value)
        self._use_camera = bool(self.get_parameter('use_camera').value)
        rgb_topic = str(self.get_parameter('rgb_topic').value)

        self._model = try_load_yolo(model_path)
        self._latest_frame = None
        self._frame_received = False

        if self._model is not None:
            self._source = 'yolo_cpu'
            self.get_logger().info(f'YOLO loaded: {model_path}')
        elif self._use_camera:
            self.get_logger().info(f'Detector idle (no model); watching {rgb_topic}')
        else:
            self.get_logger().info('Detector idle (no model, camera off)')

        if self._use_camera:
            self.create_subscription(Image, rgb_topic, self._on_image, QUEUE_DEPTH)

        self._batch_pub = self.create_publisher(DetectionBatch, DETECTION_TOPIC, QUEUE_DEPTH)
        self._hint_pub = self.create_publisher(String, HINT_TOPIC, QUEUE_DEPTH)
        rate = float(self.get_parameter('publish_rate_hz').value)
        period = 1.0 / rate if rate > 0 else 1.0
        self._timer = self.create_timer(period, self._tick)

    def _on_image(self, msg: Image) -> None:
        """Keep only the latest frame (bounded — no history buffer)."""
        self._latest_frame = image_to_bgr(msg)
        self._frame_received = True

    def _run_inference(self) -> list[Detection]:
        """Build Detection messages from YOLO or idle/wait states."""
        output: list[Detection] = []

        if self._model is None:
            idle = Detection()
            idle.label = 'camera_ready' if self._frame_received else 'idle'
            idle.confidence = 1.0
            idle.source = self._source
            return [idle]

        if self._latest_frame is not None:
            for item in detect_in_frame(self._model, self._latest_frame):
                det = Detection()
                det.label = item.label
                det.confidence = item.confidence
                det.source = 'yolo_camera'
                output.append(det)
            return output

        if self._use_camera and not self._frame_received:
            waiting = Detection()
            waiting.label = 'waiting_for_camera'
            waiting.confidence = 1.0
            waiting.source = self._source
            return [waiting]

        for item in detect_labels(self._model, self._width, self._height):
            det = Detection()
            det.label = item.label
            det.confidence = item.confidence
            det.source = self._source
            output.append(det)
        return output

    def _tick(self) -> None:
        """Publish detections and optional behavior hint."""
        batch = DetectionBatch()
        batch.header.stamp = self.get_clock().now().to_msg()
        batch.header.frame_id = 'camera'
        batch.detections.extend(self._run_inference())
        if not batch.detections:
            none_det = Detection()
            none_det.label = 'none'
            none_det.confidence = 1.0
            none_det.source = self._source
            batch.detections.append(none_det)

        self._batch_pub.publish(batch)
        hint = behavior_hint(list(batch.detections))
        if hint:
            msg = String()
            msg.data = hint
            self._hint_pub.publish(msg)


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = DetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
