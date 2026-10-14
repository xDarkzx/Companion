"""Unit tests for structured memory retrieval."""
from pathlib import Path

from companion_memory.rag_retriever import retrieve_context


def test_retrieve_kitchen(tmp_path: Path):
    places = tmp_path / 'places.yaml'
    people = tmp_path / 'people.yaml'
    places.write_text(
        'places:\n  kitchen:\n    x: 1\n    y: 2\n    yaw: 0\n',
        encoding='utf-8',
    )
    people.write_text('people:\n  dan:\n    note: owner\n', encoding='utf-8')

    used, count, summary = retrieve_context('go to kitchen', places, people)
    assert used is True
    assert count == 1
    assert 'kitchen' in summary


def test_retrieve_empty(tmp_path: Path):
    places = tmp_path / 'places.yaml'
    people = tmp_path / 'people.yaml'
    places.write_text('places: {}\n', encoding='utf-8')
    people.write_text('people: {}\n', encoding='utf-8')

    used, count, _ = retrieve_context('hello there', places, people)
    assert used is False
    assert count == 0


def test_retrieve_with_facts(tmp_path: Path):
    """Learned facts must appear in RAG summary when tokens match."""
    from companion_memory.fact_store import FactStore

    places = tmp_path / 'places.yaml'
    people = tmp_path / 'people.yaml'
    places.write_text('places: {}\n', encoding='utf-8')
    people.write_text('people: {}\n', encoding='utf-8')

    store = FactStore(tmp_path / 'facts.db')
    try:
        store.add('The garage code is 4455', 1.0)
        used, count, summary = retrieve_context(
            'what is the garage code', places, people, store
        )
        assert used is True
        assert count == 1
        assert 'fact:' in summary
        assert 'garage' in summary.lower()
    finally:
        store.close()
