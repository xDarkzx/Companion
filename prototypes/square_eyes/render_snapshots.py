"""Render a PNG snapshot of every mood (headless) for review."""
import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame

import roboeyes

SCALE = 2
OUT = Path(__file__).resolve().parent / 'snapshots'


def main():
    """Write one PNG per mood into snapshots/."""
    pygame.init()
    OUT.mkdir(exist_ok=True)
    canvas = pygame.Surface(roboeyes.CANVAS)
    color = roboeyes.PALETTES[0][1]
    for mood in roboeyes.MOODS:
        roboeyes.draw_face(canvas, mood, t=0.3, color=color)
        big = pygame.transform.scale(canvas, (roboeyes.CANVAS[0] * SCALE, roboeyes.CANVAS[1] * SCALE))
        pygame.image.save(big, str(OUT / f'{mood}.png'))
        print('wrote', mood)
    roboeyes.draw_face(canvas, 'neutral', t=0.3, color=color, blink=0.85)
    pygame.image.save(canvas, str(OUT / 'neutral_blink.png'))
    pygame.quit()


if __name__ == '__main__':
    main()
