"""Interactive PC preview of the EMO-style square-eye face.

Controls:  [<-/->] mood   [1-7] pick   [C] colour   [D] dot-matrix
           [B] blink   [SPACE] toggle 5s auto-cycle   [ESC] quit
"""
from __future__ import annotations

import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame

import roboeyes

SCALE = 2
HUD_H = 40
WIN = (roboeyes.CANVAS[0] * SCALE, roboeyes.CANVAS[1] * SCALE + HUD_H)


def main():
    """Run the interactive preview window."""
    pygame.init()
    pygame.display.set_caption(
        'Companion Face (square eyes)  |  <-/-> mood  1-7 pick  C colour  D dots  B blink  SPACE auto  ESC quit'
    )
    screen = pygame.display.set_mode(WIN)
    canvas = pygame.Surface(roboeyes.CANVAS)
    hud_font = pygame.font.SysFont('consolas', 20, bold=True)
    clock = pygame.time.Clock()

    moods, palettes = roboeyes.MOODS, roboeyes.PALETTES
    mood_i, color_i, dots, auto = 0, 0, False, True
    t0 = time.time()
    next_blink, blink_until, auto_next = t0 + 3, 0.0, t0 + 5.0

    running = True
    while running:
        now = time.time()
        t = now - t0
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
                    color_i = (color_i + 1) % len(palettes)
                elif event.key == pygame.K_d:
                    dots = not dots
                elif event.key == pygame.K_SPACE:
                    auto = not auto
                elif event.key == pygame.K_b:
                    blink_until = now + 0.15
                elif pygame.K_1 <= event.key <= pygame.K_7:
                    idx = event.key - pygame.K_1
                    if idx < len(moods):
                        mood_i = idx

        if auto and now >= auto_next:
            mood_i = (mood_i + 1) % len(moods)
            auto_next = now + 5.0
        if now >= next_blink and now > blink_until:
            blink_until = now + 0.14
            next_blink = now + random.uniform(2.5, 5.5)
        blink = max(0.0, 1 - abs((blink_until - now) / 0.14 * 2 - 1)) if now < blink_until else 0.0

        color = palettes[color_i][1]
        gaze = (int(34 * math.sin(t * 0.7)), int(18 * math.sin(t * 0.5 + 1.0)))
        roboeyes.draw_face(canvas, moods[mood_i], t, color, blink, gaze, dots)
        screen.fill((18, 18, 22))
        screen.blit(pygame.transform.scale(canvas, (roboeyes.CANVAS[0] * SCALE, roboeyes.CANVAS[1] * SCALE)), (0, 0))
        hud = f'{moods[mood_i]}   colour:{palettes[color_i][0]}   dots:{"on" if dots else "off"}   auto:{"on" if auto else "off"}'
        screen.blit(hud_font.render(hud, True, (220, 220, 235)), (12, roboeyes.CANVAS[1] * SCALE + 10))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
