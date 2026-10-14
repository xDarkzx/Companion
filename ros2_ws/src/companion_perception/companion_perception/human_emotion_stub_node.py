"""Publish HumanEmotion stub until face-affect model is wired (Phase 3)."""
from companion_interfaces.msg import HumanEmotion
import rclpy
from rclpy.node import Node

HUMAN_EMOTION_TOPIC = '/companion/human_emotion'
QUEUE_DEPTH = 10


class HumanEmotionStubNode(Node):
    """Emit neutral HumanEmotion until vision empathy model runs."""

    def __init__(self) -> None:
        """Create publisher and idle timer."""
        super().__init__('human_emotion_stub_node')
        self.declare_parameter('publish_rate_hz', 0.2)
        self.declare_parameter('default_emotion', 'neutral')
        self.declare_parameter('default_confidence', 0.5)

        self._emotion = str(self.get_parameter('default_emotion').value)
        self._confidence = float(self.get_parameter('default_confidence').value)
        self._pub = self.create_publisher(HumanEmotion, HUMAN_EMOTION_TOPIC, QUEUE_DEPTH)
        rate = float(self.get_parameter('publish_rate_hz').value)
        period = 1.0 / rate if rate > 0 else 5.0
        self._timer = self.create_timer(period, self._tick)
        self.get_logger().info('HumanEmotion stub publishing neutral affect')

    def _tick(self) -> None:
        """Publish a neutral human affect reading."""
        msg = HumanEmotion()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera'
        msg.emotion = self._emotion
        msg.confidence = self._confidence
        msg.source = 'stub'
        self._pub.publish(msg)


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = HumanEmotionStubNode()
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
