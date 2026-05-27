"""Stub Face node: logs the RobotEmotion it would render.

Phase 1 placeholder that proves the subscribe side of the pipeline. In Phase 2
the internals of this node become the real animated 8-bit LCD renderer; the
subscription contract (the RobotEmotion topic) stays identical.
"""
import rclpy
from rclpy.node import Node

from companion_interfaces.msg import RobotEmotion

ROBOT_EMOTION_TOPIC = "/companion/robot_emotion"
QUEUE_DEPTH = 10


class FaceStubNode(Node):
    """Subscribes to RobotEmotion and logs what it would display."""

    def __init__(self) -> None:
        """Create the subscription to the robot-emotion topic."""
        super().__init__("face_stub_node")
        self._subscription = self.create_subscription(
            RobotEmotion, ROBOT_EMOTION_TOPIC, self._on_emotion, QUEUE_DEPTH
        )
        self.get_logger().info(f"FaceStubNode up: listening on {ROBOT_EMOTION_TOPIC}")

    def _on_emotion(self, msg: RobotEmotion) -> None:
        """Handle an incoming emotion by logging it (placeholder for rendering)."""
        self.get_logger().info(
            f"Showing emotion: {msg.emotion} ({msg.intensity:.2f}) from {msg.source}"
        )


def main(args=None) -> None:
    """Entry point: spin the FaceStubNode with clean shutdown."""
    rclpy.init(args=args)
    node = FaceStubNode()
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
