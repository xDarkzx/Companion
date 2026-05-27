"""Pure emotion-cycling logic for the stub Brain (no ROS dependencies)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Emotion:
    """A single emotional expression: a named label and its strength (0.0-1.0)."""

    name: str
    intensity: float


def select_emotion(tick: int, sequence: list[str], intensity: float = 0.8) -> Emotion:
    """Return the Emotion for a tick by cycling through the given sequence."""
    if not sequence:
        raise ValueError('sequence must contain at least one emotion')
    if not 0.0 <= intensity <= 1.0:
        raise ValueError('intensity must be between 0.0 and 1.0')
    name = sequence[tick % len(sequence)]
    return Emotion(name=name, intensity=intensity)
