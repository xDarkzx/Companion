"""MOAT empathy bridge: HumanEmotion in → RobotEmotion out."""
from companion_brain.human_to_robot import robot_response
from companion_interfaces.msg import HumanEmotion, RobotEmotion
import rclpy
from rclpy.node import Node

HUMAN_TOPIC = '/companion/human_emotion'
ROBOT_TOPIC = '/companion/robot_emotion'
QUEUE_DEPTH = 10


class EmpathyNode(Node):
    """Translate perceived human affect into caring robot expressions."""

    def __init__(self) -> None:
        """Subscribe to human affect and publish robot emotion."""
        super().__init__('empathy_node')
        self.declare_parameter('min_confidence', 0.35)
        self._min_conf = float(self.get_parameter('min_confidence').value)
        self._pub = self.create_publisher(RobotEmotion, ROBOT_TOPIC, QUEUE_DEPTH)
        self.create_subscription(HumanEmotion, HUMAN_TOPIC, self._on_human, QUEUE_DEPTH)
        self.get_logger().info(f'EmpathyNode listening on {HUMAN_TOPIC}')

    def _on_human(self, msg: HumanEmotion) -> None:
        """Map human affect to a robot emotion response."""
        emotion, intensity = robot_response(msg.emotion, msg.confidence)
        if msg.confidence < self._min_conf:
            return

        out = RobotEmotion()
        out.header.stamp = self.get_clock().now().to_msg()
        out.emotion = emotion
        out.intensity = intensity
        out.source = 'empathy'
        self._pub.publish(out)
        self.get_logger().info(
            f'Empathy {msg.emotion}({msg.confidence:.2f}) -> {emotion}({intensity:.2f})'
        )


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = EmpathyNode()
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
