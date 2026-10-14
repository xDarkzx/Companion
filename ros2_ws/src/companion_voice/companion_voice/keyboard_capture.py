"""Read typed lines from stdin and emit them as voice commands."""
from __future__ import annotations

import sys
import threading


class KeyboardCaptureLoop:
    """Poll stdin on a daemon thread (for WSL dev without a working mic)."""

    def __init__(self, prompt: str, on_text, on_error) -> None:
        """Store prompt and callbacks."""
        self._prompt = prompt or 'Companion> '
        self._on_text = on_text
        self._on_error = on_error
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Begin reading lines until stop() is called."""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name='keyboard-capture',
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the reader thread to exit."""
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _run(self) -> None:
        """Read lines and forward non-empty text to the agent."""
        while not self._stop.is_set():
            try:
                sys.stdout.write(self._prompt)
                sys.stdout.flush()
                line = sys.stdin.readline()
            except (EOFError, OSError) as exc:
                self._on_error(str(exc))
                break
            if not line:
                break
            text = line.strip()
            if text:
                self._on_text(text)
