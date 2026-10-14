"""Unit tests for patrol face animation cycling."""
from companion_behaviors.patrol_animator import PatrolAnimation


def test_patrol_cycle_wraps():
    anim = PatrolAnimation.from_params(['neutral', 'happy'], 2.0)
    assert anim.emotion_at_tick(0) == 'neutral'
    assert anim.emotion_at_tick(1) == 'happy'
    assert anim.emotion_at_tick(2) == 'neutral'
