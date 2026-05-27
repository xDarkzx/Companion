"""Pure emotion-cycling logic for the stub Brain (no ROS dependencies).

Kept ROS-free on purpose so it can be unit tested with plain pytest on any OS,
without a running ROS graph. The ROS node is a thin wrapper around this.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Emotion:
    """A single emotional expression: a named label and its strength (0.0-1.0)."""

    name: str
    intensity: float


def select_emotion(tick: int, sequence: list[str], intensity: float = 0.8) -> Emotion:
    """Return the Emotion for a given tick by cycling through ``sequence``.

    Args:
        tick: Monotonic counter; increments once per publish.
        sequence: Ordered emotion labels to cycle through.
        intensity: Strength applied to every emotion (0.0-1.0).

    Returns:
        The Emotion selected for this tick.

    Raises:
        ValueError: If ``sequence`` is empty or ``intensity`` is out of range.
    """
    if not sequence:
        raise ValueError("sequence must contain at least one emotion")
    if not 0.0 <= intensity <= 1.0:
        raise ValueError("intensity must be between 0.0 and 1.0")
    name = sequence[tick % len(sequence)]
    return Emotion(name=name, intensity=intensity)
