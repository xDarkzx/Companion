"""Report whether MentorPi vendor drivers are installed."""
from companion_body.vendor_probe import vendor_present
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

STATUS_TOPIC = '/companion/body_status'
QUEUE_DEPTH = 10


class BodyStatusNode(Node):
    """Publish body readiness for launch orchestration."""

    def __init__(self) -> None:
        """Start periodic status publishing."""
        super().__init__('body_status_node')
        self.declare_parameter('publish_rate_hz', 1.0)
        rate = float(self.get_parameter('publish_rate_hz').value)
        self._pub = self.create_publisher(String, STATUS_TOPIC, QUEUE_DEPTH)
        self._timer = self.create_timer(1.0 / rate, self._publish)
        ready = vendor_present()
        self.get_logger().info(
            f'MentorPi vendor drivers: {"ready" if ready else "missing — run fetch script"}'
        )

    def _publish(self) -> None:
        """Emit vendor readiness string."""
        msg = String()
        msg.data = 'vendor_ready' if vendor_present() else 'vendor_missing'
        self._pub.publish(msg)


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = BodyStatusNode()
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
