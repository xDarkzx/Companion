"""WSLg PulseAudio capture/playback when PortAudio sees no devices."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

DEFAULT_PULSE_SERVER = 'unix:/mnt/wslg/PulseServer'


def pulse_server() -> str:
    """Return the WSLg PulseAudio socket path when present."""
    env = os.environ.get('PULSE_SERVER', '').strip()
    if env:
        return env
    if Path('/mnt/wslg/PulseServer').exists():
        return DEFAULT_PULSE_SERVER
    return ''


def pulse_env() -> dict[str, str]:
    """Environment with PULSE_SERVER set for parecord/paplay."""
    env = os.environ.copy()
    server = pulse_server()
    if server:
        env['PULSE_SERVER'] = server
    return env


def pulse_capture_available() -> bool:
    """True when parecord can read from WSLg RDPSource."""
    if not shutil.which('parecord'):
        return False
    if not pulse_server():
        return False
    try:
        proc = subprocess.run(
            ['pactl', 'list', 'sources', 'short'],
            capture_output=True,
            text=True,
            env=pulse_env(),
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return 'RDPSource' in proc.stdout or 'source' in proc.stdout.lower()


def record_chunk_pulse(
    seconds: float,
    sample_rate: int = 16_000,
) -> list[float]:
    """Capture mono s16le audio via parecord and return float32 samples."""
    import numpy as np

    duration = max(0.1, seconds)
    parecord_cmd = [
        'parecord',
        '--file-format=raw',
        f'--rate={sample_rate}',
        '--channels=1',
        '--format=s16le',
        '/dev/stdout',
    ]
    cmd = ['timeout', '--signal=TERM', f'{duration:.1f}s', *parecord_cmd]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        env=pulse_env(),
        timeout=duration + 5.0,
        check=False,
    )
    if not proc.stdout:
        err = proc.stderr.decode('utf-8', errors='replace')
        raise RuntimeError(err or 'parecord failed')

    samples = np.frombuffer(proc.stdout, dtype=np.int16)
    expected = int(duration * sample_rate)
    if len(samples) > expected:
        samples = samples[:expected]
    return (samples.astype(np.float32) / 32768.0).tolist()


def play_wav_pulse(wav_path: Path) -> bool:
    """Play a WAV through WSLg PulseAudio; return True on success."""
    paplay = shutil.which('paplay')
    if paplay is None:
        return False
    proc = subprocess.run(
        [paplay, str(wav_path)],
        env=pulse_env(),
        capture_output=True,
        timeout=120,
        check=False,
    )
    return proc.returncode == 0


def play_wav_pygame(wav_path: Path) -> bool:
    """Play via pygame (same path as face SFX on desktop)."""
    try:
        import pygame
    except ImportError:
        return False
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    sound = pygame.mixer.Sound(str(wav_path))
    channel = sound.play()
    if channel is None:
        return False
    import time

    while channel.get_busy():
        time.sleep(0.05)
    return True


def play_wav(wav_path: Path, output_device: str = '') -> bool:
    """Play WAV using paplay, aplay, or pygame."""
    path = Path(wav_path)
    if not path.is_file():
        return False

    if play_wav_pulse(path):
        return True

    aplay = shutil.which('aplay')
    if aplay:
        cmd = [aplay, str(path)]
        if output_device:
            cmd = [aplay, '-D', output_device, str(path)]
        if subprocess.run(cmd, check=False).returncode == 0:
            return True

    return play_wav_pygame(path)
