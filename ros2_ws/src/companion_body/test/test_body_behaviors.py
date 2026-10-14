"""Unit tests for body motion behavior mapping."""
from companion_body.body_behaviors import MOTION_BEHAVIORS, motion_status_for


def test_follow_motion_status():
    assert motion_status_for('follow') == 'motion:follow'


def test_patrol_is_motion():
    assert 'patrol' in MOTION_BEHAVIORS
    assert motion_status_for('patrol') == 'motion:patrol'


def test_idle_not_motion():
    assert motion_status_for('idle') is None
