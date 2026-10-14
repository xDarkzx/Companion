"""Unit tests for bounded SQLite fact memory."""
from pathlib import Path

from companion_memory.fact_store import FactStore


def test_add_and_search(tmp_path: Path):
    """Stored facts must match token search on later queries."""
    store = FactStore(tmp_path / 'facts.db', max_facts=10)
    try:
        store.add('The garage code is 4455', 100.0)
        hits = store.search('garage code')
        assert hits == ['The garage code is 4455']
        assert store.count() == 1
    finally:
        store.close()


def test_trim_oldest_beyond_cap(tmp_path: Path):
    """Store must drop oldest rows when max_facts is exceeded."""
    store = FactStore(tmp_path / 'facts.db', max_facts=2)
    try:
        store.add('alpha fact one', 1.0)
        store.add('beta fact two', 2.0)
        store.add('gamma fact three', 3.0)
        assert store.count() == 2
        assert store.search('gamma')
        assert not store.search('alpha')
    finally:
        store.close()


def test_search_ignores_short_tokens(tmp_path: Path):
    """Queries with only short tokens must not return arbitrary facts."""
    store = FactStore(tmp_path / 'facts.db')
    try:
        store.add('wifi password is secret', 1.0)
        assert store.search('go to') == []
        assert store.search('wifi password') == ['wifi password is secret']
    finally:
        store.close()


def test_empty_fact_not_stored(tmp_path: Path):
    """Whitespace-only facts must not create rows."""
    store = FactStore(tmp_path / 'facts.db')
    try:
        store.add('   ', 1.0)
        assert store.count() == 0
    finally:
        store.close()
