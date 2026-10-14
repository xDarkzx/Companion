"""Command grammar contract — parametrized acceptance tests for the voice parser."""
from companion_agent.parse_command import parse_command, plan_to_reply
import pytest

PLACES = frozenset({'kitchen', 'bedroom', 'dock'})


@pytest.mark.parametrize(
    ('text', 'steps'),
    [
        ('patrol', [('patrol', '')]),
        ('patrol the home', [('patrol', '')]),
        ('follow me', [('follow', '')]),
        ('go explore', [('explore', '')]),
        ('go home', [('go_home', '')]),
        ('harass the dog', [('harass_dog', '')]),
        ('stop', [('stop', '')]),
        ('stop now', [('stop', '')]),
        ('go to kitchen', [('go_to_place', 'kitchen')]),
        ('go to the bedroom', [('go_to_place', 'bedroom')]),
        ('goto dock', [('go_to_place', 'dock')]),
        ('go to kitchen and patrol', [('go_to_place', 'kitchen'), ('patrol', '')]),
        ('go to bedroom and explore', [('go_to_place', 'bedroom'), ('explore', '')]),
    ],
)
def test_valid_commands(text, steps):
    """Each accepted phrase must expand to the documented behavior plan."""
    plan = parse_command(text, PLACES)
    assert plan is not None, f'expected parse success for {text!r}'
    actual = [(s.behavior, s.target) for s in plan.steps]
    assert actual == steps


@pytest.mark.parametrize(
    'text',
    [
        'go to the garage',
        'fly to the moon',
        '',
        '   ',
        'patrol and fly',
    ],
)
def test_rejected_commands(text):
    """Unknown places and nonsense must return None (agent says sorry)."""
    assert parse_command(text, PLACES) is None


def test_plan_to_reply_matches_steps():
    """Spoken reply must mention every major step in the plan."""
    plan = parse_command('go to kitchen and patrol', PLACES)
    assert plan is not None
    reply = plan_to_reply(plan).lower()
    assert 'kitchen' in reply
    assert 'patrol' in reply
