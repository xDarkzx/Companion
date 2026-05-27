"""Stub Brain node: publishes RobotEmotion on a timer, cycling emotions.

Phase 1 placeholder that proves the publish side of the pipeline. The real
personality and empathy logic arrive in Phases 2-3; this node's published
contract (the RobotEmotion topic) will not change.
"""
import rclpy
from rclpy.node import Node

from companion_interfaces.msg import RobotEmotion

from companion_brain.emotion_cycle import select_emotion

DEFAULT_SEQUENCE = ["neutral", "happy", "sad", "angry", "love"]
ROBOT_EMOTION_TOPIC = "/companion/robot_emotion"
QUEUE_DEPTH = 10


class HeartbeatNode(Node):
    """Publishes a cycling RobotEmotion at a fixed rate (the robot's 'pulse')."""

    def __init__(self) -> None:
        """Declare parameters, create the publisher, and start the timer."""
        super().__init__("heartbeat_node")
        self.declare_parameter("publish_rate_hz", 1.0)
        self.declare_parameter("emotion_sequence", DEFAULT_SEQUENCE)
        self.declare_parameter("intensity", 0.8)

        rate_hz = self.get_parameter("publish_rate_hz").value
        self._sequence = list(self.get_parameter("emotion_sequence").value)
        self._intensity = float(self.get_parameter("intensity").value)

        self._publisher = self.create_publisher(
            RobotEmotion, ROBOT_EMOTION_TOPIC, QUEUE_DEPTH
        )
        self._tick = 0
        self._timer = self.create_timer(1.0 / rate_hz, self._on_timer)
        self.get_logger().info(
            f"HeartbeatNode up: {rate_hz} Hz, sequence={self._sequence}"
        )

    def _on_timer(self) -> None:
        """Build and publish the next RobotEmotion message."""
        emotion = select_emotion(self._tick, self._sequence, self._intensity)
        msg = RobotEmotion()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.emotion = emotion.name
        msg.intensity = float(emotion.intensity)
        msg.source = "brain"
        self._publisher.publish(msg)
        self.get_logger().info(
            f"Published emotion: {emotion.name} ({emotion.intensity})"
        )
        self._tick += 1


def main(args=None) -> None:
    """Entry point: spin the HeartbeatNode with clean shutdown."""
    rclpy.init(args=args)
    node = HeartbeatNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
