"""Record and transcribe audio with faster-whisper (Pi USB mic)."""
from __future__ import annotations

import re
import time

from companion_voice.stt_filter import filter_transcription

SAMPLE_RATE = 16_000
DEFAULT_CHUNK_SEC = 3.0
DEFAULT_MIN_RMS = 0.008
DEFAULT_POST_SPEAK_DELAY_SEC = 0.3
DEFAULT_MIN_TRANSCRIPT_WORDS = 2


def audio_rms(audio: list[float]) -> float:
    """Root-mean-square level for silence gating."""
    if not audio:
        return 0.0
    import numpy as np

    samples = np.asarray(audio, dtype=np.float32)
    return float(np.sqrt(np.mean(samples * samples)))


def log_input_devices(logger, active_index: int | None = None) -> None:
    """Log available capture devices to help fix silent mic issues."""
    try:
        import sounddevice as sd
    except ImportError:
        logger('sounddevice not installed — mic will not work')
        return

    default_in = sd.default.device[0]
    logger(f'Default input device index: {default_in}')
    for index, dev in enumerate(sd.query_devices()):
        if dev.get('max_input_channels', 0) < 1:
            continue
        marks = []
        if index == default_in:
            marks.append('default')
        if active_index is not None and index == active_index:
            marks.append('using')
        suffix = f' ({", ".join(marks)})' if marks else ''
        logger(f'  Mic [{index}]: {dev.get("name")}{suffix}')


def parse_device_index(spec: str) -> int | None:
    """Map config device string to a sounddevice input index."""
    cleaned = spec.strip()
    if not cleaned:
        return None
    if cleaned.isdigit():
        return int(cleaned)

    card_match = re.search(r'plughw:(\d+)', cleaned)
    if not card_match:
        return None

    try:
        import sounddevice as sd
    except ImportError:
        return None

    card = card_match.group(1)
    for index, dev in enumerate(sd.query_devices()):
        name = str(dev.get('name', '')).lower()
        hostapi = str(dev.get('hostapi', '')).lower()
        if dev.get('max_input_channels', 0) < 1:
            continue
        if f'hw:{card}' in name or f'card {card}' in name or card in hostapi:
            return index
    return None


def pick_input_device_index(
    devices: list[dict],
    default_index: int = -1,
    explicit_index: int | None = None,
) -> int | None:
    """Choose the first usable input device (WSL often reports default -1)."""
    if explicit_index is not None and explicit_index >= 0:
        if explicit_index < len(devices):
            if devices[explicit_index].get('max_input_channels', 0) >= 1:
                return explicit_index
        return None

    if default_index >= 0 and default_index < len(devices):
        if devices[default_index].get('max_input_channels', 0) >= 1:
            return default_index

    for index, dev in enumerate(devices):
        if dev.get('max_input_channels', 0) >= 1:
            return index
    return None


def resolve_input_device_index(spec: str) -> int | None:
    """Resolve config + system default to a valid capture device index."""
    try:
        import sounddevice as sd
    except ImportError:
        return None

    devices = list(sd.query_devices())
    default_in = int(sd.default.device[0])
    explicit = parse_device_index(spec)
    picked = pick_input_device_index(devices, default_in, explicit)
    if picked is not None:
        return picked

    from companion_voice.wslg_audio import pulse_capture_available

    if pulse_capture_available():
        return None
    return None


def use_pulse_capture() -> bool:
    """True when mic input should use parecord (WSLg) instead of sounddevice."""
    from companion_voice.wslg_audio import pulse_capture_available

    try:
        import sounddevice as sd
    except ImportError:
        return pulse_capture_available()

    default_in = int(sd.default.device[0])
    if default_in >= 0:
        return False
    return pulse_capture_available()


def record_chunk(
    seconds: float,
    sample_rate: int = SAMPLE_RATE,
    device_index: int | None = None,
) -> list[float]:
    """Capture mono float32 audio for the given duration."""
    import numpy as np
    import sounddevice as sd

    frames = int(seconds * sample_rate)
    audio = sd.rec(
        frames,
        samplerate=sample_rate,
        channels=1,
        dtype='float32',
        device=device_index,
    )
    sd.wait()
    return np.asarray(audio, dtype='float32').flatten().tolist()


def transcribe_audio(
    model,
    audio: list[float],
    sample_rate: int = SAMPLE_RATE,
    use_vad: bool = True,
    min_silence_duration_ms: int = 500,
) -> str:
    """Run faster-whisper on a mono float32 buffer (AIChatCompanion tuning)."""
    import numpy as np

    audio_np = np.asarray(audio, dtype=np.float32)
    if sample_rate != SAMPLE_RATE:
        ratio = SAMPLE_RATE / sample_rate
        new_len = int(len(audio_np) * ratio)
        audio_np = np.interp(
            np.linspace(0, len(audio_np), new_len),
            np.arange(len(audio_np)),
            audio_np,
        ).astype(np.float32)

    vad_kwargs = {}
    if use_vad:
        vad_kwargs = {
            'vad_filter': True,
            'vad_parameters': {'min_silence_duration_ms': min_silence_duration_ms},
        }

    segments, _ = model.transcribe(
        audio_np,
        language='en',
        beam_size=1,
        best_of=1,
        temperature=0.0,
        no_speech_threshold=0.6,
        condition_on_previous_text=False,
        word_timestamps=False,
        **vad_kwargs,
    )
    return ' '.join(part.text.strip() for part in segments).strip()


class WhisperCaptureLoop:
    """Poll USB mic in a daemon thread and emit recognized text."""

    def __init__(
        self,
        model_name: str,
        input_device: str,
        chunk_sec: float,
        on_text,
        on_error,
        min_audio_rms: float = DEFAULT_MIN_RMS,
        use_vad: bool = True,
        on_status=None,
        should_pause=None,
        post_speak_delay_sec: float = DEFAULT_POST_SPEAK_DELAY_SEC,
        min_transcript_words: int = DEFAULT_MIN_TRANSCRIPT_WORDS,
    ) -> None:
        """Store capture settings and callbacks."""
        import threading

        self._threading = threading
        self._model_name = model_name
        self._input_device = input_device
        self._chunk_sec = chunk_sec if chunk_sec > 0 else DEFAULT_CHUNK_SEC
        self._min_audio_rms = max(0.0, min_audio_rms)
        self._use_vad = use_vad
        self._on_text = on_text
        self._on_error = on_error
        self._on_status = on_status
        self._should_pause = should_pause
        self._post_speak_delay = max(0.0, post_speak_delay_sec)
        self._min_transcript_words = max(1, min_transcript_words)
        self._stop = threading.Event()
        self._thread = None

    def start(self) -> None:
        """Begin the capture thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = self._threading.Thread(
            target=self._run,
            daemon=True,
            name='whisper-capture',
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the capture thread to exit."""
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self._chunk_sec + 2.0)

    def _run(self) -> None:
        """Load model once, then record/transcribe until stopped."""
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            self._on_error('faster-whisper not installed')
            return

        try:
            import sounddevice  # noqa: F401
        except ImportError:
            self._on_error('sounddevice not installed')
            return

        device_index = resolve_input_device_index(self._input_device)
        pulse_mic = use_pulse_capture() and device_index is None
        emit = self._on_status or self._on_error
        if device_index is None and not pulse_mic:
            log_input_devices(emit)
            self._on_error(
                'No microphone found. WSL: enable mic in Windows Settings, '
                'then run bash scripts/desktop_mic_test.sh and set '
                'stt_node.input_device in desktop_dev.yaml'
            )
            return

        if pulse_mic:
            log_input_devices(emit)
            if self._on_status:
                self._on_status('Using WSLg mic (parecord + PulseAudio)')
        else:
            log_input_devices(emit, active_index=device_index)
            if self._on_status:
                self._on_status(f'Using mic device index {device_index}')

        model = WhisperModel(self._model_name, device='cpu', compute_type='int8')
        consecutive_errors = 0
        last_error_log = 0.0

        while not self._stop.is_set():
            try:
                if self._wait_while_paused():
                    continue

                if pulse_mic:
                    from companion_voice.wslg_audio import record_chunk_pulse

                    audio = record_chunk_pulse(self._chunk_sec, SAMPLE_RATE)
                else:
                    audio = record_chunk(self._chunk_sec, SAMPLE_RATE, device_index)
                consecutive_errors = 0
                level = audio_rms(audio)
                if level < self._min_audio_rms:
                    continue
                raw_text = transcribe_audio(
                    model,
                    audio,
                    SAMPLE_RATE,
                    use_vad=self._use_vad,
                )
                filtered = filter_transcription(
                    raw_text,
                    min_words=self._min_transcript_words,
                )
                if filtered.skipped:
                    if filtered.reason != 'empty' and self._on_status:
                        self._on_status(
                            f'Skipped STT ({filtered.reason}): {raw_text[:60]!r}'
                        )
                    continue
                self._on_text(filtered.text)
            except Exception as exc:  # noqa: BLE001 — log and keep listening
                consecutive_errors += 1
                import time

                now = time.monotonic()
                if consecutive_errors == 1 or now - last_error_log >= 5.0:
                    self._on_error(str(exc))
                    last_error_log = now
                if consecutive_errors >= 10:
                    self._on_error(
                        'Mic capture failed repeatedly; stopping STT. '
                        'Run: bash scripts/desktop_mic_test.sh'
                    )
                    return
                time.sleep(min(0.5 * consecutive_errors, 3.0))

    def _wait_while_paused(self) -> bool:
        """Block while TTS is playing; honor post-speak echo guard."""
        if self._should_pause is None:
            return False

        was_paused = False
        while not self._stop.is_set() and self._should_pause():
            was_paused = True
            time.sleep(0.05)

        if was_paused and self._post_speak_delay > 0:
            time.sleep(self._post_speak_delay)
        return was_paused
