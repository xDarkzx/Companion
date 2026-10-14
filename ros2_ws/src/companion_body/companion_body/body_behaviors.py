"""Map high-level behaviors to body-layer actions (Nav2 / motion)."""
from __future__ import annotations

# Behaviors nav_bridge handles for map-frame navigation.
NAV_MAP_BEHAVIORS = frozenset({'go_to_place', 'go_home', 'stop'})

# Behaviors that start continuous motion modes (Nav2 follow / explore — Phase 3).
MOTION_BEHAVIORS = frozenset({'follow', 'patrol', 'explore', 'harass_dog'})


def motion_status_for(behavior: str) -> str | None:
    """Return a body status string for motion behaviors, or None if not motion."""
    name = behavior.strip().lower()
    if name not in MOTION_BEHAVIORS:
        return None
    return f'motion:{name}'
