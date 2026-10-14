"""Decide when vision detection hints may trigger autonomous behaviors."""
from __future__ import annotations

from companion_agent.parse_command import CommandStep

VALID_VISION_HINTS = frozenset({'follow', 'play_with_dog'})


def should_react_to_hint(
    hint: str,
    *,
    react_enabled: bool,
    has_pending_steps: bool,
    waiting_for_nav: bool,
    cooldown_elapsed: bool,
) -> bool:
    """Return True when a detection hint may become a behavior request."""
    if not react_enabled or not cooldown_elapsed:
        return False
    if has_pending_steps or waiting_for_nav:
        return False
    return hint.strip().lower() in VALID_VISION_HINTS


def hint_to_step(hint: str) -> CommandStep | None:
    """Map a detection hint string to a behavior step, if supported."""
    behavior = hint.strip().lower()
    if behavior not in VALID_VISION_HINTS:
        return None
    return CommandStep(behavior)
