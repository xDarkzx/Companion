"""Unit tests for recognising 'where is X' requests."""
from companion_agent.find_intent import parse_find
import pytest


@pytest.mark.parametrize('text, target', [
    ('where is the mug', 'mug'),
    ("Where's my red mug?", 'red mug'),
    ('where is my phone', 'phone'),
    ('find the remote control', 'remote control'),
    ('can you see a dog', 'dog'),
    ('do you see the keys?', 'keys'),
    ('look for the cat.', 'cat'),
    ('please find my water bottle', 'water bottle'),
])
def test_find_requests_name_their_target(text, target):
    assert parse_find(text) == target


@pytest.mark.parametrize('text', [
    'go to the kitchen',
    'patrol',
    'where is',
    'find the',
    'remember that the mug is blue',
    '',
])
def test_other_commands_are_not_find_requests(text):
    assert parse_find(text) is None
