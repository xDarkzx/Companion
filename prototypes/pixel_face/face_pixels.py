"""Chunky pixel-grid robot face (24x16 'big pixels').

Crisp filled square pixels with a gap at every intersection (LCD-grid look). NO glow.
Eyes stay PUT; only blinking animates (the eye shape squashes to a line and reopens).
Each emotion is a small on/off bitmap for one eye; the other eye mirrors it (unless a
(left, right) tuple is given). '#' = lit pixel, space = off.
"""
from __future__ import annotations

import pygame

GRID_W, GRID_H = 24, 16          # big-pixel grid (landscape)
CELL = 20                        # real screen pixels per big pixel (24*20=480, 16*20=320)
GAP = 2                          # gap between big pixels -> visible LCD grid
BG = (6, 6, 10)
DEFAULT_COLOR = (60, 220, 255)
LEFT_CENTER = (6.5, 7.6)         # eye anchor centres, in grid cells
RIGHT_CENTER = (17.5, 7.6)

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
    'dots': """
 ####
######
######
######
######
 ####
""",
    'flat': """
########
########
""",
    'happy': """
   ##
  ####
 ##  ##
##    ##
""",
    'content': """
#      #
##    ##
 ######
  ####
""",
    'surprised': """
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
    'focused': """
###
###
###
###
###
###
###
""",
    'angry': """
##
 ##
  ##
  ##
 ##
##
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
    'sleepy': """
##    ##
 ######
  ####
""",
    'suspicious': """
########
########
########
########
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
    'excited': """
   ##
   ##
## ## ##
 ######
## ## ##
   ##
   ##
""",
    'dizzy': """
#      #
 ##  ##
  ####
  ####
 ##  ##
#      #
""",
    'wink': ("""
 ######
########
########
########
########
########
########
 ######
""", _CLOSED),
}

MOODS = list(_EYES.keys())


def _parse(bitmap):
    """Parse a '#'/space bitmap into (set_of_cells, width, height)."""
    lines = bitmap.split('\n')
    while lines and lines[0].strip() == '':
        lines.pop(0)
    while lines and lines[-1].strip() == '':
        lines.pop()
    width = max((len(ln) for ln in lines), default=0)
    cells = {(c, r) for r, ln in enumerate(lines) for c, ch in enumerate(ln) if ch == '#'}
    return cells, width, len(lines)


def _place(cells, width, height, center, mirror=False):
    """Centre a parsed eye on a grid anchor, optionally mirrored horizontally."""
    if mirror:
        cells = {(width - 1 - c, r) for (c, r) in cells}
    x0 = round(center[0] - width / 2)
    y0 = round(center[1] - height / 2)
    return {(x0 + c, y0 + r) for (c, r) in cells}


def _blit_cells(surface, cells, color):
    """Draw each lit grid cell as a SEPARATE pixel (gap at every intersection)."""
    for c, r in cells:
        if 0 <= c < GRID_W and 0 <= r < GRID_H:
            pygame.draw.rect(
                surface, color,
                (c * CELL + GAP // 2, r * CELL + GAP // 2, CELL - GAP, CELL - GAP),
                border_radius=3,
            )


def _squash(cells, openness):
    """Collapse the eyes vertically toward their centre row (for blinking)."""
    rows = [r for _, r in cells]
    if not rows:
        return cells
    center = (min(rows) + max(rows)) / 2
    half = (max(rows) - min(rows) + 1) * openness / 2
    kept = {(c, r) for (c, r) in cells if center - half - 0.001 <= r <= center + half + 0.001}
    if not kept:  # fully closed -> a thin line at the centre row
        cr = round(center)
        kept = {(c, cr) for (c, _) in cells}
    return kept


def draw_face(surface, mood, openness=1.0, color=DEFAULT_COLOR):
    """Render `mood` onto `surface`. openness: 1.0 = eyes open, 0.0 = closed (blink)."""
    surface.fill(BG)
    value = _EYES.get(mood, _EYES['neutral'])
    left_bm, right_bm = value if isinstance(value, tuple) else (value, value)
    lc, lw, lh = _parse(left_bm)
    rc, rw, rh = _parse(right_bm)
    cells = _place(lc, lw, lh, LEFT_CENTER) | _place(rc, rw, rh, RIGHT_CENTER, mirror=True)
    if openness < 0.999:
        cells = _squash(cells, openness)
    _blit_cells(surface, cells, color)
