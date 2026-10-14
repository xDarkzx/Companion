"""Tests for whisper audio gating and device selection."""
from companion_voice.whisper_capture import audio_rms, pick_input_device_index


def test_audio_rms_silence():
    assert audio_rms([0.0, 0.0, 0.0]) == 0.0


def test_audio_rms_signal():
    assert audio_rms([0.5, -0.5, 0.5]) > 0.4


def test_pick_input_skips_invalid_default():
    devices = [
        {'max_input_channels': 0, 'name': 'dummy'},
        {'max_input_channels': 2, 'name': 'USB Mic'},
    ]
    assert pick_input_device_index(devices, default_index=-1) == 1


def test_pick_input_honors_explicit():
    devices = [
        {'max_input_channels': 2, 'name': 'A'},
        {'max_input_channels': 2, 'name': 'B'},
    ]
    assert pick_input_device_index(devices, default_index=0, explicit_index=1) == 1


def test_pick_input_no_mics():
    devices = [{'max_input_channels': 0, 'name': 'out only'}]
    assert pick_input_device_index(devices, default_index=-1) is None


def test_filter_skips_empty_transcript():
    from companion_voice.stt_filter import filter_transcription

    assert filter_transcription('').skipped
    assert not filter_transcription('hello there').skipped
