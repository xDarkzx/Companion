"""Boot the chunky pixel-grid face. Eyes stay still; blinks on a random 2-6s timer.

Controls:  <-/->  change emotion   1-9/0  pick   C  colour   ESC  quit
(No eye movement by design -- the screen is treated as a solid pixel LCD panel.)
"""
from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame

import face_pixels as fp

SCALE = 2
COLORS = [(60, 220, 255), (120, 255, 200), (255, 190, 90), (255, 120, 200), (235, 245, 255)]
BLINK_DUR = 0.22  # seconds for a full close-and-open blink


def main():
    """Run the static pixel-face preview with random blinking."""
    pygame.init()
    base = pygame.Surface((fp.GRID_W * fp.CELL, fp.GRID_H * fp.CELL))
    screen = pygame.display.set_mode((fp.GRID_W * fp.CELL * SCALE, fp.GRID_H * fp.CELL * SCALE))
    clock = pygame.time.Clock()

    moods = fp.MOODS
    mood_i, color_i = 0, 0
    now = time.time()
    next_blink = now + random.uniform(2.0, 6.0)
    blink_until = 0.0
    auto_next = now + 5.0

    running = True
    while running:
        now = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_RIGHT:
                    mood_i = (mood_i + 1) % len(moods)
                elif event.key == pygame.K_LEFT:
                    mood_i = (mood_i - 1) % len(moods)
                elif event.key == pygame.K_c:
                    color_i = (color_i + 1) % len(COLORS)
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if idx < len(moods):
                        mood_i = idx

        if now >= auto_next:
            mood_i = (mood_i + 1) % len(moods)
            auto_next = now + 5.0
        if now >= next_blink and now > blink_until:
            blink_until = now + BLINK_DUR
            next_blink = now + random.uniform(2.0, 6.0)
        if now < blink_until:
            phase = 1.0 - (blink_until - now) / BLINK_DUR  # 0 -> 1 across the blink
            openness = abs(phase * 2.0 - 1.0)              # open -> closed -> open
        else:
            openness = 1.0

        fp.draw_face(base, moods[mood_i], openness=openness, color=COLORS[color_i])
        screen.blit(pygame.transform.scale(base, screen.get_size()), (0, 0))
        pygame.display.set_caption(
            f'Companion pixel face: {moods[mood_i]}   [<-/-> emotion, 1-9 pick, C colour, ESC quit]'
        )
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
