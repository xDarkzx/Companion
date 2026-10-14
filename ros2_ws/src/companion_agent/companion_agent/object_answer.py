"""Turn a FindObject result into one short spoken sentence."""
from __future__ import annotations

import math

STRAIGHT_AHEAD_DEG = 10.0
SLIGHTLY_DEG = 35.0


def bearing_phrase(xyz: tuple[float, float, float]) -> str:
    """Describe direction from the camera optical frame (x right, z forward)."""
    x, _y, z = xyz
    degrees = math.degrees(math.atan2(x, z))
    side = 'right' if degrees > 0 else 'left'
    if abs(degrees) < STRAIGHT_AHEAD_DEG:
        return 'straight ahead'
    if abs(degrees) < SLIGHTLY_DEG:
        return f'ahead, a little to the {side}'
    return f'to your {side}'


NO_FRAME_REASON = 'no_frame'


def answer_for(
    query: str, found: bool, xyz: tuple[float, float, float] | None, reason: str = '',
) -> str:
    """Say where the object is, that it has no distance, or why it could not be found."""
    if reason == NO_FRAME_REASON:
        return "I can't see anything yet: my camera hasn't sent a picture."
    if not found:
        return f"I can't see a {query} right now."
    if xyz is None:
        return f"I can see the {query}, but I can't tell how far away it is."
    distance = f'{math.sqrt(sum(c * c for c in xyz)):.1f}'
    unit = 'metre' if distance == '1.0' else 'metres'
    return f'The {query} is about {distance} {unit} {bearing_phrase(xyz)}.'


def answer_unavailable() -> str:
    """Say the camera service could not be reached (down, or too slow to answer)."""
    return "I can't check my camera right now."


def first_position(response) -> tuple[float, float, float] | None:
    """Return the best placed object's position from a FindObject response, if any."""
    if not response.objects.detections:
        return None
    position = response.objects.detections[0].bbox.center.position
    return (float(position.x), float(position.y), float(position.z))
