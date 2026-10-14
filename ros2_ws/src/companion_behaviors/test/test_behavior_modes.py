"""Unit tests for behavior mode validation."""
from companion_behaviors.behavior_modes import BehaviorMode, normalize_behavior
import pytest


def test_normalize_aliases():
    assert normalize_behavior('follow-me') == 'follow'
    assert normalize_behavior('play with the dog') == 'play_with_dog'


def test_invalid_behavior():
    with pytest.raises(ValueError):
        BehaviorMode('fly_to_moon')
