"""Tests for fact recall replies."""
from companion_agent.fact_recall import (
    format_recall_reply,
    looks_like_recall_query,
    try_recall_reply,
)
from companion_memory.fact_store import FactStore


def test_looks_like_recall_query():
    assert looks_like_recall_query('what is my favorite color')
    assert looks_like_recall_query('Tell me the garage code?')
    assert not looks_like_recall_query('go to kitchen')


def test_format_recall_reply():
    assert format_recall_reply('my favorite color is blue') == (
        'I remember. my favorite color is blue.'
    )


def test_try_recall_reply(tmp_path):
    store = FactStore(tmp_path / 'facts.db')
    try:
        store.add('my favorite color is blue', 1.0)
        reply = try_recall_reply('what is my favorite color', store)
        assert reply == 'I remember. my favorite color is blue.'
        assert try_recall_reply('go to kitchen', store) is None
    finally:
        store.close()


def test_try_recall_no_match(tmp_path):
    store = FactStore(tmp_path / 'facts.db')
    try:
        reply = try_recall_reply('what is my favorite color', store)
        assert reply == "I don't have that saved yet."
    finally:
        store.close()
