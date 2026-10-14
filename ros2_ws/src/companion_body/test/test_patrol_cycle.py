"""Unit tests for patrol waypoint cycling."""
from companion_body.patrol_cycle import PatrolCycle
from companion_memory.places_store import PlacePose


def _places():
    return {
        'kitchen': PlacePose('kitchen', 1.0, 2.0, 0.0),
        'bedroom': PlacePose('bedroom', 3.0, 4.0, 0.0),
    }


def test_patrol_skips_unknown_names():
    cycle = PatrolCycle(['kitchen', 'missing', 'bedroom'], _places())
    assert cycle.active
    assert cycle.current_name() == 'kitchen'


def test_patrol_advances_round_robin():
    cycle = PatrolCycle(['kitchen', 'bedroom'], _places())
    assert cycle.current_name() == 'kitchen'
    cycle.advance()
    assert cycle.current_name() == 'bedroom'
    cycle.advance()
    assert cycle.current_name() == 'kitchen'
