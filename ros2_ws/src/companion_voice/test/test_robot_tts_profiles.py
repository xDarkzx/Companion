"""Tests for robot TTS profile registry."""
from companion_voice.robot_tts_profiles import (
    DEFAULT_PROFILE_KEY,
    get_profile,
    list_profile_keys,
    ROBOT_TTS_PROFILES,
)


def test_default_profile_exists():
    get_profile(DEFAULT_PROFILE_KEY)


def test_default_profile_works_offline_without_downloads():
    assert get_profile(DEFAULT_PROFILE_KEY).backend == 'espeak'


def test_list_profiles():
    keys = list_profile_keys()
    assert 'piper_amy_chibi' in keys
    assert 'espeak_chibi' in keys


def test_only_local_open_source_engines_are_offered():
    assert {profile.backend for profile in ROBOT_TTS_PROFILES} == {'espeak', 'piper'}


def test_get_profile_espeak():
    profile = get_profile('espeak_robot')
    assert profile.backend == 'espeak'
