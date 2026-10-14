"""Tests for session chat buffer."""
from companion_memory.session_buffer import SessionBuffer


def test_bounded_size():
    buf = SessionBuffer(max_turns=3)
    for i in range(5):
        buf.add_user(f'msg{i}')
    assert len(buf) == 3
    assert buf.recent(1)[0].text == 'msg4'


def test_summary_includes_roles():
    buf = SessionBuffer(max_turns=5)
    buf.add_user('go patrol')
    buf.add_assistant('OK, patrolling.')
    assert 'user:' in buf.summary()
    assert 'assistant:' in buf.summary()
