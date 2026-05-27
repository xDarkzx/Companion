"""Render a PNG snapshot of every mood (headless) for review."""
import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame

import face_pixels as fp

OUT = Path(__file__).resolve().parent / 'snapshots'


def main():
    """Write one PNG per mood plus a blink frame."""
    pygame.init()
    OUT.mkdir(exist_ok=True)
    canvas = pygame.Surface((fp.GRID_W * fp.CELL, fp.GRID_H * fp.CELL))
    for mood in fp.MOODS:
        fp.draw_face(canvas, mood)
        pygame.image.save(canvas, str(OUT / f'{mood}.png'))
        print('wrote', mood)
    fp.draw_face(canvas, 'neutral', closed=True)
    pygame.image.save(canvas, str(OUT / 'blink.png'))
    pygame.quit()


if __name__ == '__main__':
    main()
