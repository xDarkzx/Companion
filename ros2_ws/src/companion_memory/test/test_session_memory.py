"""Session memory must augment RAG context without unbounded growth."""
from pathlib import Path

from companion_memory.rag_retriever import retrieve_context
from companion_memory.session_buffer import SessionBuffer


def test_session_summary_marks_rag_used(tmp_path: Path):
    """Recent turns must be injectable as memory context for the agent."""
    places = tmp_path / 'places.yaml'
    people = tmp_path / 'people.yaml'
    places.write_text('places:\n  kitchen:\n    x: 0\n    y: 0\n    yaw: 0\n', encoding='utf-8')
    people.write_text('people:\n  dan:\n    notes: owner\n', encoding='utf-8')

    buf = SessionBuffer(max_turns=5)
    buf.add_user('go to kitchen')
    buf.add_assistant('OK, going to the kitchen.')

    rag_used, count, summary = retrieve_context('patrol', places, people)
    session_note = buf.summary(limit=2)
    if session_note:
        summary = f'{summary}; {session_note}' if summary else session_note
        count += len(buf.recent(2))
        rag_used = True

    assert rag_used is True
    assert count >= 2
    assert 'user:' in summary
    assert 'assistant:' in summary


def test_session_drops_oldest_turns():
    """Buffer must enforce max size (memory safety rule)."""
    buf = SessionBuffer(max_turns=2)
    buf.add_user('one')
    buf.add_user('two')
    buf.add_user('three')
    assert len(buf) == 2
    assert buf.recent(1)[0].text == 'three'
