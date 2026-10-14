"""Unit tests for compound command parsing."""
from companion_agent.parse_command import parse_command, plan_to_reply

PLACES = frozenset({'kitchen', 'bedroom', 'dock'})


def test_go_to_kitchen():
    plan = parse_command('go to the kitchen', PLACES)
    assert plan is not None
    assert len(plan.steps) == 1
    assert plan.steps[0].behavior == 'go_to_place'
    assert plan.steps[0].target == 'kitchen'


def test_kitchen_then_patrol():
    plan = parse_command('go to kitchen and patrol', PLACES)
    assert plan is not None
    assert len(plan.steps) == 2
    assert plan.steps[0].behavior == 'go_to_place'
    assert plan.steps[0].target == 'kitchen'
    assert plan.steps[1].behavior == 'patrol'


def test_unknown_place():
    assert parse_command('go to the garage', PLACES) is None


def test_stop():
    plan = parse_command('stop now', PLACES)
    assert plan is not None
    assert plan.steps[0].behavior == 'stop'


def test_plan_to_reply_compound():
    plan = parse_command('go to kitchen and patrol', PLACES)
    assert plan is not None
    reply = plan_to_reply(plan)
    assert 'kitchen' in reply
    assert 'patrol' in reply.lower()


def test_plan_to_reply_stop():
    plan = parse_command('stop now', PLACES)
    assert plan is not None
    assert plan_to_reply(plan) == 'Stopping now.'
