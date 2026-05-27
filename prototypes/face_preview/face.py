"""Compose a full robot face for a given expression onto a pygame surface."""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame

import expressions
import shapes

CANVAS = (480, 320)
BG = (10, 10, 16)
EYE_CX = 240   # horizontal centre of the face
EYE_GAP = 70   # gap between the two eyes


def _eye_surface(cfg, color):
    """Build the base (un-rotated) surface for one eye from its config."""
    shape = cfg['shape']
    if shape == 'crescent_up':
        return shapes.crescent(cfg['w'], cfg['thick'], color, 'up')
    if shape == 'heart':
        return shapes.heart(cfg['w'], color)
    height = cfg['h']
    if 'lid' in cfg:
        height = max(10, int(height * (1 - cfg['lid'])))
    return shapes.rounded_eye(cfg['w'], height, cfg['r'], color)


def draw_face(surface, expression, t=0.0, color=(90, 220, 255), blink=0.0, dotmatrix=False):
    """Render the face for `expression` at time `t` onto `surface`."""
    surface.fill(BG)
    cfg = expressions.CONFIG.get(expression, expressions.CONFIG['neutral'])
    bob = int(3 * math.sin(t * 2.0))
    tilt = cfg.get('tilt', 0)

    for side in ('left', 'right'):
        eye = _eye_surface(cfg, color)
        if cfg.get('wink') and side == 'right':
            eye = shapes.crescent(cfg['w'], 40, color, 'up')
        elif blink > 0.01 and cfg['shape'] == 'rounded':
            ew, eh = eye.get_size()
            eye = pygame.transform.smoothscale(eye, (ew, max(6, int(eh * (1 - 0.92 * blink)))))
        angle = tilt if side == 'left' else -tilt
        if angle:
            eye = pygame.transform.rotozoom(eye, angle, 1.0)
        ew, eh = eye.get_size()
        sign = -1 if side == 'left' else 1
        cx = EYE_CX + sign * (EYE_GAP // 2 + cfg['w'] // 2)
        cy = cfg.get('cy', 160) + bob
        surface.blit(eye, (cx - ew // 2, cy - eh // 2))

    expressions.draw_extras(surface, cfg.get('extras', ()), t, color)
    if dotmatrix:
        _overlay_dotmatrix(surface)


def _overlay_dotmatrix(surface):
    """Darken a thin grid over the canvas for a 'semi dot-matrix' LED feel."""
    w, h = surface.get_size()
    grid = pygame.Surface((w, h), pygame.SRCALPHA)
    line = (0, 0, 0, 70)
    for x in range(0, w, 8):
        pygame.draw.line(grid, line, (x, 0), (x, h))
    for y in range(0, h, 8):
        pygame.draw.line(grid, line, (0, y), (w, y))
    surface.blit(grid, (0, 0))
