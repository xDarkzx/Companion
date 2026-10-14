"""Unit tests for stdin keyboard capture."""
from companion_voice.keyboard_capture import KeyboardCaptureLoop


def test_keyboard_loop_start_and_stop():
    """Capture thread must start and stop cleanly without hanging."""
    loop = KeyboardCaptureLoop('> ', lambda _text: None, lambda _msg: None)
    loop.start()
    loop.stop()
    assert loop._thread is None or not loop._thread.is_alive()  # noqa: SLF001
