"""Desktop camera + detection overlay window (PC prototype visualization)."""
from __future__ import annotations

from companion_face.preview_labels import format_detection_lines
from companion_interfaces.msg import DetectionBatch
import numpy as np
import pygame
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

DETECTION_TOPIC = '/companion/detections'
QUEUE_DEPTH = 10
DEFAULT_RGB_TOPIC = '/image_raw'


def ros_image_to_surface(msg: Image):
    """Convert a sensor_msgs/Image to a pygame Surface, or None if unsupported."""
    encoding = msg.encoding.lower()
    if encoding == 'rgb8':
        channels = 3
        swap = None
    elif encoding in {'bgr8', 'bgra8'}:
        channels = 3 if encoding == 'bgr8' else 4
        swap = slice(None, None, -1)
    elif encoding == 'mono8':
        channels = 1
        swap = None
    else:
        return None

    expected = msg.width * msg.height * channels
    if len(msg.data) < expected:
        return None

    array = np.frombuffer(msg.data, dtype=np.uint8, count=expected)
    if channels == 1:
        rgb = np.stack([array.reshape(msg.height, msg.width)] * 3, axis=-1)
    else:
        frame = array.reshape(msg.height, msg.width, channels)
        rgb = frame[:, :, :3] if channels == 4 else frame
        if swap is not None:
            rgb = rgb[:, :, swap]

    return pygame.image.frombuffer(
        rgb.tobytes(),
        (msg.width, msg.height),
        'RGB',
    )


class VisionPreviewNode(Node):
    """Show live camera frames with YOLO detection labels (PC dev only)."""

    def __init__(self) -> None:
        """Subscribe to camera + detections and cache the latest samples."""
        super().__init__('vision_preview_node')
        self.declare_parameter('rgb_topic', DEFAULT_RGB_TOPIC)
        self.declare_parameter('display_scale', 1)

        rgb_topic = str(self.get_parameter('rgb_topic').value)
        self._scale = max(1, int(self.get_parameter('display_scale').value))
        self._latest_image: pygame.Surface | None = None
        self._status_lines = ['waiting for camera…']
        self._camera_seen = False

        self.create_subscription(Image, rgb_topic, self._on_image, QUEUE_DEPTH)
        self.create_subscription(
            DetectionBatch,
            DETECTION_TOPIC,
            self._on_detections,
            QUEUE_DEPTH,
        )
        self.get_logger().info(
            f'Vision preview on {rgb_topic} + {DETECTION_TOPIC}'
        )

    def _on_image(self, msg: Image) -> None:
        """Cache the latest frame for the pygame render loop."""
        surface = ros_image_to_surface(msg)
        if surface is not None:
            self._latest_image = surface
            self._camera_seen = True

    def _on_detections(self, msg: DetectionBatch) -> None:
        """Cache formatted labels for the overlay panel."""
        self._status_lines = format_detection_lines(list(msg.detections))

    def draw(self, canvas: pygame.Surface) -> None:
        """Paint camera frame and detection status onto the canvas."""
        canvas.fill((16, 20, 28))
        if self._latest_image is not None:
            canvas.blit(self._latest_image, (0, 0))
        else:
            self._draw_message(canvas, 'Waiting for /image_raw…')

        self._draw_panel(canvas, self._status_lines)

    def _draw_message(self, canvas: pygame.Surface, text: str) -> None:
        """Center a short status message when no frame is available."""
        font = pygame.font.SysFont('consolas', 18)
        label = font.render(text, True, (200, 210, 220))
        canvas.blit(label, (12, 12))

    def _draw_panel(self, canvas: pygame.Surface, lines: list[str]) -> None:
        """Draw a translucent detection list over the bottom of the frame."""
        font = pygame.font.SysFont('consolas', 16)
        panel_h = 24 + len(lines) * 20
        panel = pygame.Surface((canvas.get_width(), panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 170))
        canvas.blit(panel, (0, canvas.get_height() - panel_h))

        title = 'Detections' if self._camera_seen else 'Vision'
        title_y = canvas.get_height() - panel_h + 4
        canvas.blit(font.render(title, True, (120, 200, 255)), (10, title_y))
        y = canvas.get_height() - panel_h + 24
        for line in lines:
            canvas.blit(font.render(line, True, (230, 230, 230)), (10, y))
            y += 20


def main(args=None) -> None:
    """Run pygame preview loop alongside ROS subscriptions."""
    rclpy.init(args=args)
    node = VisionPreviewNode()
    pygame.init()
    width, height = 640, 480
    scale = max(1, int(node.get_parameter('display_scale').value))
    screen = pygame.display.set_mode((width * scale, height * scale))
    canvas = pygame.Surface((width, height))
    clock = pygame.time.Clock()

    try:
        running = True
        while rclpy.ok() and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            rclpy.spin_once(node, timeout_sec=0)
            node.draw(canvas)
            if scale == 1:
                screen.blit(canvas, (0, 0))
            else:
                screen.blit(pygame.transform.scale(canvas, screen.get_size()), (0, 0))
            pygame.display.set_caption('Companion vision preview')
            pygame.display.flip()
            clock.tick(30)
    finally:
        node.destroy_node()
        pygame.quit()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
