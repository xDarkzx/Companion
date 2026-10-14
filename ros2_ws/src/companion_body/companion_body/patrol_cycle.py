"""Cycle patrol through named places from memory."""
from __future__ import annotations

from companion_memory.places_store import PlacePose


class PatrolCycle:
    """Bounded round-robin over configured place names."""

    def __init__(self, place_names: list[str], places: dict[str, PlacePose]) -> None:
        """Keep only names that exist in the places map."""
        self._names = [n for n in place_names if n in places]
        self._places = places
        self._index = 0

    @property
    def active(self) -> bool:
        """Return True when at least one patrol waypoint exists."""
        return bool(self._names)

    def current(self) -> PlacePose | None:
        """Return the active patrol place, if any."""
        if not self._names:
            return None
        name = self._names[self._index % len(self._names)]
        return self._places.get(name)

    def current_name(self) -> str:
        """Return the active place name or empty string."""
        if not self._names:
            return ''
        return self._names[self._index % len(self._names)]

    def advance(self) -> PlacePose | None:
        """Move to the next waypoint and return it."""
        if not self._names:
            return None
        self._index = (self._index + 1) % len(self._names)
        return self.current()
