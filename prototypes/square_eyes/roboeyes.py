"""EMO / RoboEyes-style square-eye renderer.

Two rounded-square glowing eyes on black; mood comes from 'eyelid' cuts that
reshape the SAME eye (not different cartoon shapes). Anti-aliased via 2x
supersampling, with a soft glow. Clean, consistent, robotic.
"""
from __future__ import annotations

import math

import pygame

CANVAS = (480, 320)
BG = (8, 8, 12)
EYE_W = 124
EYE_H = 124
RADIUS = 40
GAP = 60
CY = 158
PAD = 46
SS = 2  # supersample factor for smooth edges

MOODS = ['neutral', 'happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted']
PALETTES = [
    ('cyan', (80, 225, 255)),
    ('mint', (120, 255, 200)),
    ('amber', (255, 190, 90)),
    ('pink', (255, 130, 200)),
    ('white', (230, 245, 255)),
]

# Per-mood eye size scale (w, h) relative to the base square.
_SCALE = {
    'neutral': (1.0, 1.0),
    'happy': (1.0, 1.0),
    'sad': (0.96, 0.84),
    'angry': (1.04, 0.96),
    'surprised': (1.08, 1.26),
    'fearful': (0.92, 1.22),
    'disgusted': (1.0, 0.96),
}


def _blur(surf, factor=0.18):
    """Cheap blur by down/up scaling (used for the glow)."""
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, int(w * factor)), max(1, int(h * factor))))
    return pygame.transform.smoothscale(small, (w, h))


def _cut(eye, points):
    """Erase a filled polygon region from the eye (an eyelid)."""
    lid = pygame.Surface(eye.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(lid, (0, 0, 0, 255), points)
    eye.blit(lid, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


def _cut_ellipse(eye, rect):
    """Erase a filled ellipse region from the eye (curved eyelid)."""
    lid = pygame.Surface(eye.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(lid, (0, 0, 0, 255), rect)
    eye.blit(lid, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


def _apply_lids(eye, mood, side, rect):
    """Carve the mood into the eye using eyelid cuts. rect = (x, y, w, h)."""
    x0, y0, w, h = rect
    sw, sh = eye.get_size()
    top = y0
    if mood == 'happy':
        _cut_ellipse(eye, (x0 - w * 0.35, y0 + h * 0.36, w * 1.7, h * 1.7))
    elif mood == 'angry':
        drop = h * 0.74
        if side == 'left':  # inner edge (right) drops
            _cut(eye, [(0, 0), (sw, 0), (sw, top + drop), (0, top)])
        else:               # inner edge (left) drops
            _cut(eye, [(0, 0), (sw, 0), (sw, top), (0, top + drop)])
    elif mood == 'sad':
        drop = h * 0.5
        if side == 'left':  # outer edge (left) droops
            _cut(eye, [(0, 0), (sw, 0), (sw, top), (0, top + drop)])
        else:
            _cut(eye, [(0, 0), (sw, 0), (sw, top + drop), (0, top)])
    elif mood == 'fearful':
        _cut(eye, [(0, 0), (sw, 0), (sw, top + h * 0.16), (0, top + h * 0.16)])
    elif mood == 'disgusted':
        # one raised brow: heavy slant on the right eye, light on the left
        drop = h * (0.62 if side == 'right' else 0.22)
        if side == 'left':
            _cut(eye, [(0, 0), (sw, 0), (sw, top), (0, top + drop)])
        else:
            _cut(eye, [(0, 0), (sw, 0), (sw, top + drop), (0, top)])


def _eye_surface(mood, side, color, blink):
    """Build one glowing, mood-shaped eye surface (anti-aliased)."""
    sx, sy = _SCALE.get(mood, (1.0, 1.0))
    ew, eh = int(EYE_W * sx), int(EYE_H * sy)
    pad = PAD
    sw, sh = (ew + 2 * pad) * SS, (eh + 2 * pad) * SS
    rect = (pad * SS, pad * SS, ew * SS, eh * SS)
    eye = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.rect(eye, (*color, 255), pygame.Rect(*rect), border_radius=RADIUS * SS)
    _apply_lids(eye, mood, side, rect)
    if blink > 0.01:
        close = int((eh * SS / 2) * blink)
        lid = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.rect(lid, (0, 0, 0, 255), (0, 0, sw, pad * SS + close))
        pygame.draw.rect(lid, (0, 0, 0, 255), (0, (pad + eh) * SS - close, sw, sh))
        eye.blit(lid, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    eye = pygame.transform.smoothscale(eye, ((ew + 2 * pad), (eh + 2 * pad)))
    glow = _blur(eye, 0.18)
    out = pygame.Surface(eye.get_size(), pygame.SRCALPHA)
    out.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    out.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    out.blit(eye, (0, 0))
    return out


def _overlay_dotmatrix(surface):
    """Optional faint LED-grid overlay."""
    w, h = surface.get_size()
    grid = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(0, w, 8):
        pygame.draw.line(grid, (0, 0, 0, 55), (x, 0), (x, h))
    for y in range(0, h, 8):
        pygame.draw.line(grid, (0, 0, 0, 55), (0, y), (w, y))
    surface.blit(grid, (0, 0))


def draw_face(surface, mood, t=0.0, color=(80, 225, 255), blink=0.0, gaze=(0, 0), dotmatrix=False):
    """Render both eyes for `mood` onto `surface`."""
    surface.fill(BG)
    bob = int(2 * math.sin(t * 2.0))
    gx, gy = gaze
    for side in ('left', 'right'):
        eye = _eye_surface(mood, side, color, blink)
        ew, eh = eye.get_size()
        sign = -1 if side == 'left' else 1
        cx = 240 + sign * (GAP // 2 + EYE_W // 2) + gx
        cy = CY + bob + gy
        surface.blit(eye, (cx - ew // 2, cy - eh // 2))
    if dotmatrix:
        _overlay_dotmatrix(surface)
