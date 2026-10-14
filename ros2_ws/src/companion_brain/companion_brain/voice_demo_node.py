"""Demo: fake voice events -> needy/playful RobotEmotion publishes."""
from __future__ import annotations

from companion_brain.personality import PersonalityState, react_to_voice, VoiceEvent
from companion_interfaces.msg import RobotEmotion
import rclpy
from rclpy.node import Node

TOPIC = '/companion/robot_emotion'
QUEUE_DEPTH = 10
DEMO_EVENTS = [
    VoiceEvent.WAKE,
    VoiceEvent.PRAISE,
    VoiceEvent.IGNORE,
    VoiceEvent.IGNORE,
    VoiceEvent.SILENCE,
    VoiceEvent.PLAY,
    VoiceEvent.SCOLD,
    VoiceEvent.COMMAND_FAIL,
]


class VoiceDemoNode(Node):
    """Publish emotions as if reacting to voice — until real STT exists."""

    def __init__(self) -> None:
        super().__init__('voice_demo_node')
        self.declare_parameter('interval_s', 3.0)
        interval = float(self.get_parameter('interval_s').value)
        self._pub = self.create_publisher(RobotEmotion, TOPIC, QUEUE_DEPTH)
        self._state = PersonalityState()
        self._i = 0
        self._timer = self.create_timer(interval, self._tick)
        self.get_logger().info('VoiceDemoNode: needy/playful emotion demo at %.1fs' % interval)

    def _tick(self) -> None:
        event = DEMO_EVENTS[self._i % len(DEMO_EVENTS)]
        self._i += 1
        emo, self._state = react_to_voice(event, self._state)
        msg = RobotEmotion()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.emotion = emo.name
        msg.intensity = float(emo.intensity)
        msg.source = 'voice_demo:%s' % event.value
        self._pub.publish(msg)
        self.get_logger().info('voice %s -> %s (%.2f)' % (event.value, emo.name, emo.intensity))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VoiceDemoNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
