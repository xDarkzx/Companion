"""Text-to-speech on the MentorPi WonderEcho USB speaker."""
from companion_interfaces.msg import RobotEmotion
from companion_voice.tts_engine import describe_tts, resolve_tts_mode, speak
from companion_voice.tts_paths import discover_piper_model
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

TTS_TOPIC = '/companion/tts_request'
TTS_PLAYING_TOPIC = '/companion/tts_playing'
EMOTION_TOPIC = '/companion/robot_emotion'
QUEUE_DEPTH = 10


class TtsNode(Node):
    """Play agent replies via phrase clips, Piper, espeak, or log-only mode."""

    def __init__(self) -> None:
        """Subscribe to TTS requests and track face emotion for expressivity."""
        super().__init__('tts_node')
        self.declare_parameter('mode', 'log')
        self.declare_parameter('output_device', '')
        self.declare_parameter('piper_model', '')
        self.declare_parameter('phrase_assets_dir', '')

        self._mode = str(self.get_parameter('mode').value)
        self._output_device = str(self.get_parameter('output_device').value)
        self._phrase_dir = str(self.get_parameter('phrase_assets_dir').value)
        configured_model = str(self.get_parameter('piper_model').value)
        self._piper_model = discover_piper_model(configured_model)
        self._resolved_mode = resolve_tts_mode(
            self._mode,
            self._piper_model,
            phrase_dir=self._phrase_dir,
        )
        self._last_emotion = 'neutral'

        self.create_subscription(String, TTS_TOPIC, self._on_tts, QUEUE_DEPTH)
        self.create_subscription(
            RobotEmotion, EMOTION_TOPIC, self._on_emotion, QUEUE_DEPTH
        )
        self._playing_pub = self.create_publisher(Bool, TTS_PLAYING_TOPIC, QUEUE_DEPTH)
        if self._resolved_mode == 'log' and self._mode.strip().lower() in {'', 'auto'}:
            self.get_logger().warn(
                'No TTS engine found — speech is log-only. '
                'Run: bash scripts/fetch_robot_phrases.sh'
            )
        self.get_logger().info(
            f'TTS mode={self._mode} (resolved={self._resolved_mode}) '
            f'{describe_tts(self._phrase_dir)} on {TTS_TOPIC}'
        )

    def _on_emotion(self, msg: RobotEmotion) -> None:
        """Remember the latest face mood for expressivity knobs."""
        if msg.emotion:
            self._last_emotion = msg.emotion

    def _set_playing(self, active: bool) -> None:
        """Tell STT to pause while audio is playing."""
        msg = Bool()
        msg.data = active
        self._playing_pub.publish(msg)

    def _on_tts(self, msg: String) -> None:
        """Handle a speak request."""
        self._set_playing(True)
        try:
            outcome = speak(
                msg.data,
                self._mode,
                self._piper_model,
                self._output_device,
                emotion=self._last_emotion,
                phrase_dir=self._phrase_dir,
            )
        finally:
            self._set_playing(False)

        if outcome == 'logged':
            self.get_logger().info(f'TTS would speak: {msg.data[:120]!r}')
        elif outcome == 'cached':
            self.get_logger().info(f'TTS cached ({self._last_emotion}): {msg.data[:80]!r}')
        elif outcome == 'failed':
            self.get_logger().error(f'TTS failed: {msg.data[:120]!r}')
        else:
            self.get_logger().info(
                f'TTS {outcome} ({self._last_emotion}): {msg.data[:80]!r}'
            )


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = TtsNode()
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
