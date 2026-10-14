"""Unit tests for intent routing."""
from companion_agent.intent_router import route_intent


def test_follow_me():
    assert route_intent('hey buddy follow me') == 'follow'


def test_patrol():
    assert route_intent('go patrol the home please') == 'patrol'


def test_harass_dog():
    assert route_intent('go harass the dog') == 'harass_dog'


def test_unknown():
    assert route_intent('make me a sandwich') is None
