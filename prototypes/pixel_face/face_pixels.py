"""Chunky pixel-grid robot face (24x16 'big pixels').

Crisp filled square pixels only -- NO glow, NO blur. Eyes stay PUT; only blinking
animates. Each emotion is a small on/off bitmap for one eye; the other eye mirrors it
(unless a (left, right) tuple is given). '#' = lit pixel, space = off.
"""
from __future__ import annotations

import pygame

GRID_W, GRID_H = 24, 16          # big-pixel grid (landscape)
CELL = 20                        # real screen pixels per big pixel (24*20=480, 16*20=320)
GAP = 2                          # gap between big pixels for the LED-grid look
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
    'happy': """
#      #
##    ##
 ##  ##
 ######
  ####
""",
    'sad': """
      ##
   #####
 #######
########
########
########
########
 ######
""",
    'angry': """
##
#####
#######
########
########
########
########
 ######
""",
    'surprised': """
 ######
########
########
########
########
########
########
########
########
 ######
""",
    'fearful': """
 ####
######
######
######
######
######
######
######
 ####
""",
    'sleepy': """
########
########
########
""",
    'suspicious': """
########
########
########
########
""",
    'bored': """

########
########
""",
    'excited': """
  ####
 ######
########
########
########
########
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
    'dizzy': """
#      #
##    ##
 ##  ##
  ####
  ####
 ##  ##
##    ##
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


def _blur(surf, factor=0.22):
    """Down/up-scale to make the soft glow halo (used behind the crisp pixels)."""
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, int(w * factor)), max(1, int(h * factor))))
    return pygame.transform.smoothscale(small, (w, h))


def draw_face(surface, mood, closed=False, color=DEFAULT_COLOR):
    """Render the face for `mood` (or a blink when closed=True) onto `surface`.

    Crisp square pixels with a soft glow halo radiating behind them.
    """
    surface.fill(BG)
    if closed:
        left_bm = right_bm = _CLOSED
    else:
        value = _EYES.get(mood, _EYES['neutral'])
        left_bm, right_bm = value if isinstance(value, tuple) else (value, value)
    lc, lw, lh = _parse(left_bm)
    rc, rw, rh = _parse(right_bm)
    cells = _place(lc, lw, lh, LEFT_CENTER) | _place(rc, rw, rh, RIGHT_CENTER, mirror=True)
    _blit_cells(surface, cells, color)
