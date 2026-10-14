"""ROS node: ASCII blue-eye face driven by /companion/robot_emotion."""
from __future__ import annotations

from pathlib import Path
import random
import time

from companion_face.ascii_renderer import (
    draw_cloud_badge,
    draw_face,
    draw_status_line,
    lcd_surface,
)
from companion_face.mood_map import mood_for_emotion
from companion_face.sfx_player import SfxPlayer
from companion_interfaces.msg import AgentState, RobotEmotion
from companion_memory.rag_state import state_needs_cloud_indicator
import pygame
import rclpy
from rclpy.node import Node

TOPIC = '/companion/robot_emotion'
STATE_TOPIC = '/companion/agent_state'
QUEUE_DEPTH = 10
BLINK_DUR = 0.22


class FaceAsciiNode(Node):
    """Render RobotEmotion on a 480x320 pygame window with random blinks + SFX."""

    def __init__(self) -> None:
        super().__init__('face_ascii_node')
        self.declare_parameter('display_scale', 1)
        self.declare_parameter('enable_sfx', True)
        self.declare_parameter('blink_min_s', 2.0)
        self.declare_parameter('blink_max_s', 5.5)
        self.declare_parameter('sfx_assets_dir', '')

        self._emotion = 'neutral'
        self._intensity = 0.8
        self._scale = int(self.get_parameter('display_scale').value)
        sfx_dir = str(self.get_parameter('sfx_assets_dir').value)
        self._sfx = SfxPlayer(
            bool(self.get_parameter('enable_sfx').value),
            assets_dir=sfx_dir,
        )
        if sfx_dir:
            from companion_face.sfx_bank import list_loaded_sfx

            loaded = list_loaded_sfx(Path(sfx_dir))
            self.get_logger().info(
                'SFX assets dir=%s loaded=%s' % (sfx_dir, loaded or '(synth fallback)')
            )
        self._blink_min = float(self.get_parameter('blink_min_s').value)
        self._blink_max = float(self.get_parameter('blink_max_s').value)

        self._next_blink = time.time() + random.uniform(self._blink_min, self._blink_max)
        self._blink_until = 0.0
        self._last_emotion = ''
        self._agent_state = 'idle'
        self._last_agent_state = 'idle'
        self._agent_provider = 'none'
        self._agent_status = ''
        self._cloud_pulse = 0.0

        self.create_subscription(RobotEmotion, TOPIC, self._on_emotion, QUEUE_DEPTH)
        self.create_subscription(AgentState, STATE_TOPIC, self._on_agent_state, QUEUE_DEPTH)
        self.get_logger().info('FaceAsciiNode listening on %s + %s' % (TOPIC, STATE_TOPIC))

    def _on_emotion(self, msg: RobotEmotion) -> None:
        self._emotion = msg.emotion
        self._intensity = float(msg.intensity)
        if msg.emotion != self._last_emotion:
            self.get_logger().info('Face -> %s (%.2f)' % (msg.emotion, msg.intensity))
            if msg.emotion.lower() == 'sleepy':
                self._sfx.play_yawn()
            else:
                self._sfx.play_for_emotion(msg.emotion)
            self._last_emotion = msg.emotion

    def _on_agent_state(self, msg: AgentState) -> None:
        """Track LLM/RAG state for cloud badge overlay and react beeps."""
        prev = self._agent_state
        self._agent_state = msg.state
        self._agent_provider = msg.provider
        self._agent_status = msg.status_text
        if msg.state != prev:
            self._play_state_sfx(msg.state)
        self._last_agent_state = msg.state

    def _play_state_sfx(self, state: str) -> None:
        """Play short beeps when the agent starts listening or thinking."""
        from companion_face.sfx_bank import AGENT_STATE_SFX

        key = AGENT_STATE_SFX.get(state, '')
        if key:
            self._sfx._play_key(key)

    def blink_openness(self, now: float) -> float:
        if now >= self._next_blink and now > self._blink_until:
            self._blink_until = now + BLINK_DUR
            self._next_blink = now + random.uniform(self._blink_min, self._blink_max)
            self._sfx.play_blink()
        if now < self._blink_until:
            phase = 1.0 - (self._blink_until - now) / BLINK_DUR
            return abs(phase * 2.0 - 1.0)
        return 1.0

    def draw(self, surface: pygame.Surface, now: float) -> None:
        mood = mood_for_emotion(self._emotion)
        if state_needs_cloud_indicator(self._agent_state):
            mood = 'surprise'
        draw_face(surface, mood, openness=self.blink_openness(now))
        pulse = 0.5 + 0.5 * abs((now * 2.0) % 1.0 - 0.5) * 2.0
        self._cloud_pulse = pulse
        draw_cloud_badge(
            surface,
            state_needs_cloud_indicator(self._agent_state),
            pulse=pulse,
        )
        if self._agent_status and self._agent_state != 'idle':
            draw_status_line(surface, self._agent_status)


def main(args=None) -> None:
    """Spin pygame render loop + ROS subscription."""
    rclpy.init(args=args)
    node = FaceAsciiNode()
    pygame.init()
    base = lcd_surface()
    w, h = base.get_size()
    scale = max(1, int(node.get_parameter('display_scale').value))
    screen = pygame.display.set_mode((w * scale, h * scale))
    clock = pygame.time.Clock()

    try:
        running = True
        while rclpy.ok() and running:
            now = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            rclpy.spin_once(node, timeout_sec=0)
            node.draw(base, now)
            if scale == 1:
                screen.blit(base, (0, 0))
            else:
                screen.blit(pygame.transform.scale(base, screen.get_size()), (0, 0))
            pygame.display.set_caption('Companion ASCII face — %s' % node._emotion)
            pygame.display.flip()
            clock.tick(60)
    finally:
        node.destroy_node()
        pygame.quit()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
