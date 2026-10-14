"""Tests for vision hint gating before autonomous behaviors."""
from companion_agent.vision_react import hint_to_step, should_react_to_hint


def test_follow_hint_when_idle():
    assert should_react_to_hint(
        'follow',
        react_enabled=True,
        has_pending_steps=False,
        waiting_for_nav=False,
        cooldown_elapsed=True,
    )


def test_ignored_during_nav():
    assert not should_react_to_hint(
        'follow',
        react_enabled=True,
        has_pending_steps=False,
        waiting_for_nav=True,
        cooldown_elapsed=True,
    )


def test_ignored_during_plan():
    assert not should_react_to_hint(
        'follow',
        react_enabled=True,
        has_pending_steps=True,
        waiting_for_nav=False,
        cooldown_elapsed=True,
    )


def test_ignored_when_disabled():
    assert not should_react_to_hint(
        'follow',
        react_enabled=False,
        has_pending_steps=False,
        waiting_for_nav=False,
        cooldown_elapsed=True,
    )


def test_ignored_during_cooldown():
    assert not should_react_to_hint(
        'follow',
        react_enabled=True,
        has_pending_steps=False,
        waiting_for_nav=False,
        cooldown_elapsed=False,
    )


def test_hint_to_step_maps_dog():
    step = hint_to_step('harass_dog')
    assert step is not None
    assert step.behavior == 'harass_dog'


def test_unknown_hint_returns_none():
    assert hint_to_step('idle') is None
