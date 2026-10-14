"""Unit tests for RAG/LLM state helpers."""
from companion_memory.rag_state import state_needs_cloud_indicator


def test_cloud_indicator_on_thinking():
    assert state_needs_cloud_indicator('thinking') is True
    assert state_needs_cloud_indicator('idle') is False
