"""Apply BehaviorRequest commands: emotion, patrol animations, status."""
from companion_behaviors.behavior_modes import (
    BEHAVIOR_EMOTIONS,
    BehaviorMode,
    normalize_behavior,
    VALID_BEHAVIORS,
)
from companion_behaviors.patrol_animator import PatrolAnimation
from companion_interfaces.msg import BehaviorRequest, RobotEmotion
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

BEHAVIOR_TOPIC = '/companion/behavior_request'
STATUS_TOPIC = '/companion/behavior_status'
EMOTION_TOPIC = '/companion/robot_emotion'
QUEUE_DEPTH = 10


class BehaviorControllerNode(Node):
    """Translate behavior requests into face emotion and body status strings."""

    def __init__(self) -> None:
        """Wire subscribers, publishers, and patrol animation timer."""
        super().__init__('behavior_controller_node')
        self.declare_parameter('patrol_emotions', ['neutral', 'surprise', 'happy'])
        self.declare_parameter('patrol_animation_sec', 2.5)

        self._active = BehaviorMode('idle')
        self._patrol_tick = 0
        self._patrol_anim = PatrolAnimation.from_params(
            list(self.get_parameter('patrol_emotions').value),
            float(self.get_parameter('patrol_animation_sec').value),
        )

        self._emotion_pub = self.create_publisher(
            RobotEmotion, EMOTION_TOPIC, QUEUE_DEPTH
        )
        self._status_pub = self.create_publisher(String, STATUS_TOPIC, QUEUE_DEPTH)
        self.create_subscription(
            BehaviorRequest, BEHAVIOR_TOPIC, self._on_request, QUEUE_DEPTH
        )
        self._patrol_timer = self.create_timer(
            self._patrol_anim.interval_sec, self._on_patrol_tick
        )
        self._patrol_timer.cancel()
        self.get_logger().info('BehaviorControllerNode ready')

    def _on_request(self, msg: BehaviorRequest) -> None:
        """Switch behavior and publish emotion + status."""
        name = msg.behavior.strip().lower()
        if name not in VALID_BEHAVIORS:
            name = normalize_behavior(name)
        try:
            self._active = BehaviorMode(name, float(msg.intensity))
        except ValueError as exc:
            self.get_logger().warn(str(exc))
            return

        if name == 'patrol':
            self._patrol_tick = 0
            self._patrol_timer.reset()
        else:
            self._patrol_timer.cancel()

        self._publish_emotion(
            BEHAVIOR_EMOTIONS.get(name, 'neutral'),
            float(self._active.intensity),
            msg.source or 'behaviors',
        )

        target = msg.target.strip() if msg.target else ''
        status = String()
        if target:
            status.data = f'active:{name}:{target}'
        else:
            status.data = f'active:{name}'
        self._status_pub.publish(status)
        self.get_logger().info(
            f'Behavior {name} target={target!r} ({msg.source})'
        )

    def _on_patrol_tick(self) -> None:
        """Cycle patrol face animations while patrolling."""
        if self._active.name != 'patrol':
            return
        emotion_name = self._patrol_anim.emotion_at_tick(self._patrol_tick)
        self._publish_emotion(emotion_name, self._active.intensity, 'patrol_anim')
        self._patrol_tick += 1

    def _publish_emotion(self, emotion_name: str, intensity: float, source: str) -> None:
        """Publish a RobotEmotion message."""
        emotion = RobotEmotion()
        emotion.header.stamp = self.get_clock().now().to_msg()
        emotion.emotion = emotion_name
        emotion.intensity = intensity
        emotion.source = source
        self._emotion_pub.publish(emotion)


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = BehaviorControllerNode()
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
