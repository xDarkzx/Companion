"""Structured + fact memory lookup for the agent RAG path."""
from pathlib import Path

from companion_memory.fact_store import FactStore
from companion_memory.people_store import load_people
from companion_memory.places_store import load_places


def retrieve_context(
    text: str,
    places_file: Path,
    people_file: Path,
    fact_store: FactStore | None = None,
) -> tuple[bool, int, str]:
    """Return (rag_used, chunk_count, summary) from YAML + optional fact store."""
    lowered = text.lower()
    hits: list[str] = []

    for name in load_places(places_file):
        if name in lowered or name.replace('_', ' ') in lowered:
            hits.append(f'place:{name}')

    for name in load_people(people_file):
        if name in lowered:
            hits.append(f'person:{name}')

    if fact_store is not None:
        for fact in fact_store.search(text):
            hits.append(f'fact:{fact[:40]}')

    if not hits:
        return False, 0, ''
    return True, len(hits), ', '.join(hits[:5])
