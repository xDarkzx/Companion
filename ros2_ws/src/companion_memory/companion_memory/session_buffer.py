"""Bounded in-memory chat history (Tier 2 session memory)."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatTurn:
    """One user or assistant utterance in the current session."""

    role: str
    text: str


class SessionBuffer:
    """Store the last N conversation turns without unbounded growth."""

    def __init__(self, max_turns: int = 20) -> None:
        """Create a fixed-size session buffer."""
        self._max = max(1, max_turns)
        self._turns: deque[ChatTurn] = deque(maxlen=self._max)

    def add_user(self, text: str) -> None:
        """Record a user voice/text command."""
        cleaned = text.strip()
        if cleaned:
            self._turns.append(ChatTurn('user', cleaned))

    def add_assistant(self, text: str) -> None:
        """Record a spoken or logged assistant reply."""
        cleaned = text.strip()
        if cleaned:
            self._turns.append(ChatTurn('assistant', cleaned))

    def recent(self, limit: int = 5) -> tuple[ChatTurn, ...]:
        """Return the most recent turns (oldest first within the slice)."""
        if limit <= 0:
            return ()
        return tuple(list(self._turns)[-limit:])

    def summary(self, limit: int = 3) -> str:
        """Build a short context string for RAG / LLM injection."""
        parts = [f'{turn.role}: {turn.text[:60]}' for turn in self.recent(limit)]
        return '; '.join(parts)

    def __len__(self) -> int:
        """Return the number of stored turns."""
        return len(self._turns)
