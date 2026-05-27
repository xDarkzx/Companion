"""Low-level pygame shape primitives for the robot eyes (glow, eye, crescent, heart)."""
from __future__ import annotations

import pygame

PAD = 48  # padding around each shape to leave room for the glow halo


def blur(surface: pygame.Surface, factor: float = 0.18) -> pygame.Surface:
    """Return a cheap blurred copy by downscaling then upscaling."""
    w, h = surface.get_size()
    small = pygame.transform.smoothscale(
        surface, (max(1, int(w * factor)), max(1, int(h * factor)))
    )
    return pygame.transform.smoothscale(small, (w, h))


def _with_glow(base: pygame.Surface, passes: int = 2) -> pygame.Surface:
    """Composite an additive glow (blurred copy) behind an opaque shape."""
    out = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    glow = blur(base, 0.16)
    for _ in range(passes):
        out.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    out.blit(base, (0, 0))
    return out


def rounded_eye(w: int, h: int, radius: int, color, highlight: bool = True) -> pygame.Surface:
    """Build a glowing rounded-rectangle eye with anime-style highlights."""
    surf = pygame.Surface((w + 2 * PAD, h + 2 * PAD), pygame.SRCALPHA)
    pygame.draw.rect(surf, (*color, 255), pygame.Rect(PAD, PAD, w, h), border_radius=radius)
    surf = _with_glow(surf)
    if highlight:
        pygame.draw.ellipse(
            surf, (255, 255, 255, 245),
            (PAD + int(w * 0.18), PAD + int(h * 0.12), int(w * 0.36), int(h * 0.26)),
        )
    return surf


def crescent(width: int, thickness: int, color, direction: str = 'up') -> pygame.Surface:
    """Build a glowing crescent eye ('up' = happy smile, 'down' = frown)."""
    radius = width // 2
    size = width + 2 * PAD
    center = (PAD + radius, PAD + radius)
    disc = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(disc, (*color, 255), center, radius)
    cut = pygame.Surface((size, size), pygame.SRCALPHA)
    dy = -thickness if direction == 'up' else thickness
    pygame.draw.circle(cut, (255, 255, 255, 255), (center[0], center[1] + dy), radius)
    disc.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return _with_glow(disc)


def heart(size: int, color, highlight: bool = True) -> pygame.Surface:
    """Build a glowing heart eye (used for the 'love' expression)."""
    span = size + 2 * PAD
    base = pygame.Surface((span, span), pygame.SRCALPHA)
    r = size // 4
    cx = PAD + size // 2
    top = PAD + r
    pygame.draw.circle(base, (*color, 255), (cx - r, top), r)
    pygame.draw.circle(base, (*color, 255), (cx + r, top), r)
    pygame.draw.polygon(base, (*color, 255), [(PAD, top), (PAD + size, top), (cx, PAD + size)])
    surf = _with_glow(base)
    if highlight:
        pygame.draw.ellipse(surf, (255, 255, 255, 200), (cx - r, top - r // 2, r, r // 2))
    return surf
