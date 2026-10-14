"""Unit tests for remember-that voice command parsing."""
from companion_agent.remember_command import parse_remember_fact


def test_remember_that_phrase():
    """Standard remember-that form extracts the fact text."""
    assert parse_remember_fact('Remember that the cat is named Pixel') == (
        'the cat is named Pixel'
    )


def test_remember_without_that():
    """Shorter remember form still captures the fact."""
    assert parse_remember_fact('remember wifi password is abc123') == (
        'wifi password is abc123'
    )


def test_dont_forget_variant():
    """Don't-forget phrasing maps to the same fact path."""
    assert parse_remember_fact("Don't forget that dinner is at six") == (
        'dinner is at six'
    )


def test_non_remember_returns_none():
    """Normal navigation commands must not be treated as facts."""
    assert parse_remember_fact('go to kitchen') is None
    assert parse_remember_fact('') is None
