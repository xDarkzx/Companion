"""Interactive PC preview of the Companion robot face (run on Windows or any desktop).

Controls:  [<-/->] change expression   [1-9] pick   [C] eye colour
           [D] toggle dot-matrix        [B] blink    [SPACE] auto-cycle   [ESC] quit
"""
from __future__ import annotations

import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame

import expressions
import face

SCALE = 2
HUD_H = 40
WIN = (face.CANVAS[0] * SCALE, face.CANVAS[1] * SCALE + HUD_H)


def main():
    """Run the interactive preview window."""
    pygame.init()
    pygame.display.set_caption(
        'Companion Face  |  <-/-> expr  1-9 pick  C colour  D dots  B blink  SPACE auto  ESC quit'
    )
    screen = pygame.display.set_mode(WIN)
    canvas = pygame.Surface(face.CANVAS)
    hud_font = pygame.font.SysFont('consolas', 20, bold=True)
    clock = pygame.time.Clock()

    order, palettes = expressions.ORDER, expressions.PALETTES
    expr_i, color_i, dots, auto = 0, 0, True, True
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
                    expr_i = (expr_i + 1) % len(order)
                elif event.key == pygame.K_LEFT:
                    expr_i = (expr_i - 1) % len(order)
                elif event.key == pygame.K_c:
                    color_i = (color_i + 1) % len(palettes)
                elif event.key == pygame.K_d:
                    dots = not dots
                elif event.key == pygame.K_SPACE:
                    auto = not auto
                elif event.key == pygame.K_b:
                    blink_until = now + 0.15
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if idx < len(order):
                        expr_i = idx

        if auto and now >= auto_next:
            expr_i = (expr_i + 1) % len(order)
            auto_next = now + 5.0
        if now >= next_blink and now > blink_until:
            blink_until = now + 0.14
            next_blink = now + random.uniform(2.5, 5.5)
        blink = max(0.0, 1 - abs((blink_until - now) / 0.14 * 2 - 1)) if now < blink_until else 0.0

        color = palettes[color_i][1]
        gaze = (int(36 * math.sin(t * 0.8)), int(22 * math.sin(t * 0.55 + 1.0)))
        face.draw_face(canvas, order[expr_i], t, color, blink, dots, gaze)
        screen.fill((18, 18, 22))
        screen.blit(pygame.transform.scale(canvas, (face.CANVAS[0] * SCALE, face.CANVAS[1] * SCALE)), (0, 0))
        hud = f'{order[expr_i]}   colour:{palettes[color_i][0]}   dots:{"on" if dots else "off"}   auto:{"on" if auto else "off"}'
        screen.blit(hud_font.render(hud, True, (220, 220, 235)), (12, face.CANVAS[1] * SCALE + 10))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
