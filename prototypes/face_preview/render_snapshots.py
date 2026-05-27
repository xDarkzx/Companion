"""Render a PNG snapshot of every expression (headless) so the look can be reviewed."""
import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame

import expressions
import face

SCALE = 2
OUT = Path(__file__).resolve().parent / 'snapshots'


def main():
    """Write one PNG per expression (plus a blink frame) into snapshots/."""
    pygame.init()
    OUT.mkdir(exist_ok=True)
    canvas = pygame.Surface(face.CANVAS)
    color = expressions.PALETTES[0][1]
    for name in expressions.ORDER:
        face.draw_face(canvas, name, t=0.4, color=color, blink=0.0, dotmatrix=True)
        big = pygame.transform.scale(canvas, (face.CANVAS[0] * SCALE, face.CANVAS[1] * SCALE))
        pygame.image.save(big, str(OUT / f'{name}.png'))
        print('wrote', name)
    face.draw_face(canvas, 'neutral', t=0.4, color=color, blink=0.85, dotmatrix=True)
    pygame.image.save(canvas, str(OUT / 'neutral_blink.png'))
    pygame.quit()
    print('snapshots in', OUT)


if __name__ == '__main__':
    main()
