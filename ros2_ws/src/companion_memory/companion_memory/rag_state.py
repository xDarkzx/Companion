"""Explicit RAG / LLM lifecycle states for the companion agent."""
from dataclasses import dataclass

VALID_STATES = frozenset({
    'idle',
    'listening',
    'retrieving',
    'thinking',
    'speaking',
    'acting',
    'error',
})

CLOUD_ACTIVE_STATES = frozenset({'retrieving', 'thinking', 'speaking'})


@dataclass(frozen=True)
class RagTurnContext:
    """One conversational turn with optional retrieved memories."""

    user_text: str
    rag_used: bool = False
    memory_count: int = 0
    provider: str = 'none'


def state_needs_cloud_indicator(state: str) -> bool:
    """Return True when the face should show the cloud-thinking badge."""
    return state in CLOUD_ACTIVE_STATES
