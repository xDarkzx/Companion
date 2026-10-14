"""Speech-to-text bridge — publishes /companion/voice_command."""
from companion_interfaces.msg import AgentState
from companion_voice.keyboard_capture import KeyboardCaptureLoop
from companion_voice.whisper_capture import WhisperCaptureLoop
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

COMMAND_TOPIC = '/companion/voice_command'
STATE_TOPIC = '/companion/agent_state'
TTS_PLAYING_TOPIC = '/companion/tts_playing'
QUEUE_DEPTH = 10


class SttNode(Node):
    """Capture speech and emit text commands (keyboard stub until Whisper on Pi)."""

    def __init__(self) -> None:
        """Wire topics and select STT mode."""
        super().__init__('stt_node')
        self.declare_parameter('mode', 'keyboard')
        self.declare_parameter('input_device', '')
        self.declare_parameter('whisper_model', 'base.en')
        self.declare_parameter('keyboard_prompt', 'Companion> ')
        self.declare_parameter('chunk_sec', 3.0)
        self.declare_parameter('min_audio_rms', 0.008)
        self.declare_parameter('use_vad', True)
        self.declare_parameter('post_speak_delay_sec', 0.3)
        self.declare_parameter('min_transcript_words', 2)

        self._mode = str(self.get_parameter('mode').value)
        self._tts_playing = False
        self._command_pub = self.create_publisher(String, COMMAND_TOPIC, QUEUE_DEPTH)
        self._state_pub = self.create_publisher(AgentState, STATE_TOPIC, QUEUE_DEPTH)
        self._capture: WhisperCaptureLoop | None = None
        self._keyboard: KeyboardCaptureLoop | None = None
        self.create_subscription(Bool, TTS_PLAYING_TOPIC, self._on_tts_playing, QUEUE_DEPTH)
        self.get_logger().info(f'STT mode={self._mode}')

        if self._mode == 'whisper':
            self._start_whisper()
        elif self._mode == 'keyboard':
            self._start_keyboard()
        else:
            self.get_logger().warn(f'Unknown stt mode {self._mode!r}; idle')

    def _on_tts_playing(self, msg: Bool) -> None:
        """Pause mic capture while the robot is speaking (echo guard)."""
        self._tts_playing = bool(msg.data)

    def _mic_should_pause(self) -> bool:
        """Report whether TTS playback is active."""
        return self._tts_playing

    def publish_text(self, text: str) -> None:
        """Send recognized text to the agent pipeline."""
        cleaned = text.strip()
        if not cleaned:
            return

        listening = AgentState()
        listening.header.stamp = self.get_clock().now().to_msg()
        listening.state = 'listening'
        listening.status_text = cleaned[:40]
        self._state_pub.publish(listening)

        msg = String()
        msg.data = cleaned
        self._command_pub.publish(msg)
        self.get_logger().info(f'STT -> {cleaned!r}')

    def _start_whisper(self) -> None:
        """Start USB mic capture with faster-whisper on a background thread."""
        model_name = str(self.get_parameter('whisper_model').value)
        input_device = str(self.get_parameter('input_device').value)
        chunk_sec = float(self.get_parameter('chunk_sec').value)
        min_rms = float(self.get_parameter('min_audio_rms').value)
        use_vad = bool(self.get_parameter('use_vad').value)
        post_delay = float(self.get_parameter('post_speak_delay_sec').value)
        min_words = int(self.get_parameter('min_transcript_words').value)

        self._capture = WhisperCaptureLoop(
            model_name=model_name,
            input_device=input_device,
            chunk_sec=chunk_sec,
            min_audio_rms=min_rms,
            use_vad=use_vad,
            on_text=self.publish_text,
            on_error=self._on_capture_error,
            on_status=self._on_capture_status,
            should_pause=self._mic_should_pause,
            post_speak_delay_sec=post_delay,
            min_transcript_words=min_words,
        )
        self._capture.start()
        self.get_logger().info(
            f'Whisper capture started model={model_name} device={input_device!r}'
        )

    def _start_keyboard(self) -> None:
        """Read typed lines from stdin when no mic is available."""
        prompt = str(self.get_parameter('keyboard_prompt').value)
        self._keyboard = KeyboardCaptureLoop(
            prompt=prompt,
            on_text=self.publish_text,
            on_error=self._on_capture_error,
        )
        self._keyboard.start()
        self.get_logger().info('Keyboard mode: type commands at the prompt')

    def _on_capture_error(self, message: str) -> None:
        """Log capture failures without stopping the node."""
        self.get_logger().error(f'Whisper capture: {message}')

    def _on_capture_status(self, message: str) -> None:
        """Log mic setup and readiness info."""
        self.get_logger().info(f'Whisper: {message}')

    def destroy_node(self) -> bool:
        """Stop capture thread before ROS teardown."""
        if self._capture is not None:
            self._capture.stop()
            self._capture = None
        if self._keyboard is not None:
            self._keyboard.stop()
            self._keyboard = None
        return super().destroy_node()


def main(args=None) -> None:
    """Spin with clean shutdown."""
    rclpy.init(args=args)
    node = SttNode()
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
