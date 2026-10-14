"""Monitor MentorPi depth camera streams and publish companion status."""
from companion_perception.camera_status import compute_camera_status, STALE_NS
from companion_perception.mentorpi_camera import (
    DEPTH_IMAGE_TOPIC,
    RGB_IMAGE_TOPIC,
)
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

CAMERA_STATUS_TOPIC = '/companion/camera_status'
QUEUE_DEPTH = 10


class CameraWatchNode(Node):
    """Track RGB/depth frame freshness for the deluxe depth camera kit."""

    def __init__(self) -> None:
        """Subscribe to vendor camera topics and publish status."""
        super().__init__('camera_watch_node')
        self.declare_parameter('rgb_topic', RGB_IMAGE_TOPIC)
        self.declare_parameter('depth_topic', DEPTH_IMAGE_TOPIC)
        self.declare_parameter('status_rate_hz', 1.0)

        rgb_topic = str(self.get_parameter('rgb_topic').value)
        depth_topic = str(self.get_parameter('depth_topic').value)
        rate = float(self.get_parameter('status_rate_hz').value)

        self._rgb_seen = False
        self._depth_seen = False
        self._last_rgb_ns = 0
        self._last_depth_ns = 0

        self._status_pub = self.create_publisher(String, CAMERA_STATUS_TOPIC, QUEUE_DEPTH)
        self.create_subscription(Image, rgb_topic, self._on_rgb, QUEUE_DEPTH)
        self.create_subscription(Image, depth_topic, self._on_depth, QUEUE_DEPTH)
        period = 1.0 / rate if rate > 0 else 1.0
        self._timer = self.create_timer(period, self._publish_status)

        self.get_logger().info(
            f'Watching RGB={rgb_topic} depth={depth_topic}'
        )

    def _on_rgb(self, _msg: Image) -> None:
        """Record RGB frame arrival."""
        self._rgb_seen = True
        self._last_rgb_ns = self.get_clock().now().nanoseconds

    def _on_depth(self, _msg: Image) -> None:
        """Record depth frame arrival."""
        self._depth_seen = True
        self._last_depth_ns = self.get_clock().now().nanoseconds

    def _publish_status(self) -> None:
        """Publish human-readable camera health for the agent stack."""
        now_ns = self.get_clock().now().nanoseconds
        status = compute_camera_status(
            self._rgb_seen,
            self._depth_seen,
            self._last_rgb_ns,
            self._last_depth_ns,
            now_ns,
            STALE_NS,
        )

        msg = String()
        msg.data = status
        self._status_pub.publish(msg)


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = CameraWatchNode()
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
