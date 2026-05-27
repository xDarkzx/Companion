"""Expression definitions and animated anime-style 'extras' for the robot face."""
from __future__ import annotations

import math

import pygame

# Colour palettes the eyes can use (name, RGB). Cycle with [C] in the preview.
PALETTES = [
    ('cyan', (90, 220, 255)),
    ('mint', (120, 255, 200)),
    ('amber', (255, 190, 90)),
    ('pink', (255, 130, 200)),
    ('white', (235, 245, 255)),
]

# Each expression says how the two eyes are drawn + which extras to overlay.
#   shape: 'rounded' | 'crescent_up' | 'heart'
#   tilt : degrees applied to the LEFT eye (right eye mirrored) -> eyebrow mood
#   lid  : 0..1 fraction of the eye covered (sleepy)
# Geometry is in the logical 480x320 canvas.
CONFIG = {
    'neutral':  dict(shape='rounded', w=104, h=140, r=44, tilt=0, cy=150),
    'happy':    dict(shape='crescent_up', w=128, thick=46, tilt=0, cy=140, mouth='smile'),
    'sad':      dict(shape='rounded', w=100, h=116, r=42, tilt=18, cy=160, mouth='frown', extras=('teardrop',)),
    'angry':    dict(shape='rounded', w=112, h=108, r=24, tilt=-22, cy=150, extras=('vein',)),
    'cry':      dict(shape='rounded', w=100, h=120, r=42, tilt=18, cy=158, mouth='frown', extras=('tears',)),
    'love':     dict(shape='heart', w=120, tilt=0, cy=156, extras=('hearts',)),
    'surprise': dict(shape='rounded', w=132, h=150, r=62, tilt=0, cy=156, extras=('excl',)),
    'sleepy':   dict(shape='rounded', w=110, h=140, r=46, tilt=0, cy=170, lid=0.6, extras=('zzz',)),
    'yawn':     dict(shape='crescent_up', w=120, thick=30, tilt=0, cy=150, extras=('zzz',)),
    'wink':     dict(shape='rounded', w=104, h=140, r=44, tilt=0, cy=160, wink=True),
}

ORDER = ['neutral', 'happy', 'sad', 'angry', 'cry', 'love', 'surprise', 'sleepy', 'yawn', 'wink']

_FONTS: dict[int, pygame.font.Font] = {}


def _font(size: int) -> pygame.font.Font:
    """Return a cached bold font, initialising the font system if needed."""
    if not pygame.font.get_init():
        pygame.font.init()
    if size not in _FONTS:
        _FONTS[size] = pygame.font.SysFont('consolas', size, bold=True)
    return _FONTS[size]


def _drop(surface, x, y, scale=1.0):
    """Draw a single teardrop at (x, y)."""
    blue = (120, 200, 255)
    r = int(7 * scale)
    pygame.draw.circle(surface, blue, (x, y + r), r)
    pygame.draw.polygon(surface, blue, [(x - r, y + r), (x + r, y + r), (x, y - r)])


def _mini_heart(surface, x, y, s, color, alpha):
    """Draw a small translucent heart centred at (x, y)."""
    tmp = pygame.Surface((2 * s, 2 * s), pygame.SRCALPHA)
    r = s // 2
    cx, top = s, r + 2
    pygame.draw.circle(tmp, color, (cx - r // 2, top), r // 2 + 2)
    pygame.draw.circle(tmp, color, (cx + r // 2, top), r // 2 + 2)
    pygame.draw.polygon(tmp, color, [(cx - r, top), (cx + r, top), (cx, top + s)])
    tmp.set_alpha(alpha)
    surface.blit(tmp, (x - s, y - s))


def _vein(surface, t, color):
    """Anime 'pop vein' anger mark (top-right), gently pulsing."""
    cx, cy = 360, 70
    red = (255, 80, 80)
    size = int(16 + 3 * math.sin(t * 8))
    for ang in (210, 270, 330, 30, 90, 150):
        rad = math.radians(ang)
        x1 = cx + int(math.cos(rad) * 6)
        y1 = cy + int(math.sin(rad) * 6)
        x2 = cx + int(math.cos(rad) * size)
        y2 = cy + int(math.sin(rad) * size)
        pygame.draw.line(surface, red, (x1, y1), (x2, y2), 5)


def _teardrop(surface, t, color):
    """A single welling tear under the inner left eye."""
    _drop(surface, 178, 214 + int((t * 36) % 70), 1.1)


def _tears(surface, t, color):
    """Streaming tears under both eyes."""
    for i, x in enumerate((176, 322)):
        for k in range(3):
            y = 206 + int((t * 130 + k * 38 + i * 19) % 115)
            _drop(surface, x, y, 1.0)


def _hearts(surface, t, color):
    """Pink hearts floating up (love)."""
    pink = (255, 120, 190)
    for i in range(4):
        phase = (t * 0.6 + i * 0.27) % 1.0
        x = 130 + i * 70 + int(10 * math.sin(t * 2 + i))
        y = 250 - int(phase * 180)
        _mini_heart(surface, x, y, 16, pink, max(0, int(255 * (1 - phase))))


def _excl(surface, t, color):
    """A bouncing exclamation mark above the eyes (surprise)."""
    yellow = (255, 230, 90)
    x = 240
    y = 40 + int(4 * math.sin(t * 6))
    pygame.draw.rect(surface, yellow, (x - 5, y, 10, 26), border_radius=4)
    pygame.draw.circle(surface, yellow, (x, y + 38), 6)


def _zzz(surface, t, color):
    """Rising 'Z's for sleepy/yawn."""
    blue = (160, 205, 255)
    for i in range(3):
        phase = (t * 0.5 + i * 0.33) % 1.0
        img = _font(26).render('Z', True, blue)
        img = pygame.transform.rotozoom(img, 0, 0.8 + 0.35 * i)
        img.set_alpha(max(0, int(230 * (1 - phase))))
        surface.blit(img, (330 + i * 20, 120 - int(phase * 70) - i * 16))


_EXTRAS = {
    'vein': _vein,
    'teardrop': _teardrop,
    'tears': _tears,
    'hearts': _hearts,
    'excl': _excl,
    'zzz': _zzz,
}


def draw_extras(surface, names, t, color):
    """Draw each named animated extra onto the canvas."""
    for name in names:
        _EXTRAS[name](surface, t, color)
