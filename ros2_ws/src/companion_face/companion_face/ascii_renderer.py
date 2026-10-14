"""Blue square-grid eyes on black — procedural blink, no image assets."""
from __future__ import annotations

import pygame

GRID_W, GRID_H = 24, 16
CELL = 20
GAP = 2
BG = (0, 0, 0)
EYE_COLOR = (60, 220, 255)

_CLOSED = """
########
########
"""

_EYES = {
    'neutral': """
 ######
########
########
########
########
########
########
 ######
""",
    'happy': """
   ##
  ####
 ##  ##
##    ##
""",
    'sad': """
......##
....####
..######
########
########
########
 ######
""",
    'angry': """
##
 ##
  ##
  ##
 ##
##
""",
    'cry': """
 ####
######
######
######
 ####
""",
    'love': """
 ##  ##
########
########
########
 ######
  ####
   ##
""",
    'surprise': """
#####
#####
#####
#####
#####
#####
#####
#####
#####
#####
""",
    'sleepy': """
##    ##
 ######
  ####
""",
    'wink': (
        """
 ######
########
########
########
########
########
########
 ######
""",
        _CLOSED,
    ),
}

LEFT_CENTER = (6.5, 7.6)
RIGHT_CENTER = (17.5, 7.6)


def _parse(bitmap: str) -> tuple[set[tuple[int, int]], int, int]:
    lines = [ln for ln in bitmap.split('\n') if ln.strip()]
    width = max((len(ln) for ln in lines), default=0)
    cells = {(c, r) for r, ln in enumerate(lines) for c, ch in enumerate(ln) if ch == '#'}
    return cells, width, len(lines)


def _place(cells, width, height, center, mirror=False):
    if mirror:
        cells = {(width - 1 - c, r) for (c, r) in cells}
    x0 = round(center[0] - width / 2)
    y0 = round(center[1] - height / 2)
    return {(x0 + c, y0 + r) for (c, r) in cells}


def _blit_cells(surface, cells, color):
    for c, r in cells:
        if 0 <= c < GRID_W and 0 <= r < GRID_H:
            pygame.draw.rect(
                surface,
                color,
                (c * CELL + GAP // 2, r * CELL + GAP // 2, CELL - GAP, CELL - GAP),
            )


def _squash(cells, openness):
    rows = [r for _, r in cells]
    if not rows:
        return cells
    center = (min(rows) + max(rows)) / 2
    half = (max(rows) - min(rows) + 1) * openness / 2
    kept = {(c, r) for (c, r) in cells if center - half - 0.001 <= r <= center + half + 0.001}
    if not kept:
        cr = round(center)
        kept = {(c, cr) for (c, _) in cells}
    return kept


def draw_face(surface, mood: str, openness: float = 1.0, color=EYE_COLOR) -> None:
    """Draw mood eyes; openness 1.0=open, 0.0=closed blink."""
    surface.fill(BG)
    key = mood if mood in _EYES else 'neutral'
    value = _EYES[key]
    left_bm, right_bm = value if isinstance(value, tuple) else (value, value)
    lc, lw, lh = _parse(left_bm)
    rc, rw, rh = _parse(right_bm)
    cells = _place(lc, lw, lh, LEFT_CENTER) | _place(rc, rw, rh, RIGHT_CENTER, mirror=True)
    if openness < 0.999:
        cells = _squash(cells, openness)
    _blit_cells(surface, cells, color)


_CLOUD = (120, 200, 255)
_BADGE = (40, 40, 40)


def draw_cloud_badge(surface, active: bool, pulse: float = 1.0) -> None:
    """Top-right cloud-active indicator (Emo-style, Companion-branded dots)."""
    if not active:
        return
    x0 = GRID_W * CELL - 56
    y0 = 8
    pygame.draw.rect(surface, _BADGE, (x0 - 4, y0 - 4, 52, 28), border_radius=6)
    alpha = int(180 + 75 * max(0.0, min(1.0, pulse)))
    dot_r = max(3, int(5 * pulse))
    for i, dx in enumerate((8, 22, 36)):
        shade = (
            min(255, _CLOUD[0] + i * 20),
            min(255, _CLOUD[1]),
            min(255, _CLOUD[2] + alpha // 8),
        )
        pygame.draw.circle(surface, shade, (x0 + dx, y0 + 12), dot_r)


def draw_status_line(surface, text: str) -> None:
    """Draw a one-line status hint under the eyes."""
    if not text:
        return
    try:
        font = pygame.font.SysFont('consolas', 14)
    except Exception:
        return
    label = font.render(text[:40], True, (90, 90, 90))
    surface.blit(label, (8, GRID_H * CELL - 22))


def lcd_surface() -> pygame.Surface:
    """Native 480x320 grid buffer."""
    return pygame.Surface((GRID_W * CELL, GRID_H * CELL))
