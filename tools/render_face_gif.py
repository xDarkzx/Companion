"""Render the robot's real face renderer off-screen into docs/media/face.gif.

The storyboard follows what the face shows during "where is the mug?": idle, searching (cloud
badge and status line, as AgentState 'retrieving' draws it), answering, then other moods.
Usage: python tools/render_face_gif.py
"""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'ros2_ws' / 'src' / 'companion_face'))
OUTPUT = REPO / 'docs' / 'media' / 'face.gif'
FPS = 12
BLINK_FRAMES = 3


@dataclass(frozen=True)
class Shot:
    """One stretch of the animation."""

    mood: str
    seconds: float
    cloud: bool = False
    status: str = ''
    blink: bool = False


def storyboard() -> list[Shot]:
    """The sequence the README animation shows."""
    return [
        Shot('neutral', 1.5, blink=True),
        Shot('surprise', 1.5, cloud=True, status='looking for mug'),
        Shot('happy', 2.0, status='The mug is about 1.5 metres ahead'),
        Shot('love', 1.0),
        Shot('sad', 1.0),
        Shot('angry', 1.0),
        Shot('sleepy', 1.2, blink=True),
    ]


def render_frames(shots: list[Shot]):
    """Draw every frame with the production renderer and return PIL images."""
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    import pygame
    from PIL import Image

    from companion_face.ascii_renderer import (
        draw_cloud_badge,
        draw_face,
        draw_status_line,
        lcd_surface,
    )

    pygame.init()
    surface = lcd_surface()
    frames = []
    for shot in shots:
        count = round(shot.seconds * FPS)
        blink_at = count // 2
        for index in range(count):
            openness = 1.0
            if shot.blink and blink_at <= index < blink_at + BLINK_FRAMES:
                openness = abs((index - blink_at) / (BLINK_FRAMES - 1) * 2.0 - 1.0)
            draw_face(surface, shot.mood, openness=openness)
            draw_cloud_badge(surface, shot.cloud, pulse=0.5 + 0.5 * (index % FPS) / FPS)
            if shot.status:
                draw_status_line(surface, shot.status)
            raw = pygame.image.tostring(surface, 'RGB')
            frames.append(Image.frombytes('RGB', surface.get_size(), raw))
    pygame.quit()
    return frames


def main() -> None:
    """Write the animated GIF."""
    frames = render_frames(storyboard())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUTPUT, save_all=True, append_images=frames[1:], loop=0,
                   duration=round(1000 / FPS), optimize=True)
    print(OUTPUT, f'{OUTPUT.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
