"""Play TTS on the MentorPi WonderEcho USB speaker."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from companion_voice.tts_emotion import PiperEmotionProfile
from companion_voice.tts_paths import discover_piper_binary


def _speak_piper(
    text: str,
    model_path: str,
    output_device: str,
    profile: PiperEmotionProfile,
) -> str:
    """Run Piper ONNX TTS with emotion-aware synthesis knobs."""
    piper_bin = discover_piper_binary()
    if not piper_bin or not model_path or not Path(model_path).is_file():
        return 'failed'

    aplay_bin = shutil.which('aplay')
    if aplay_bin is None:
        return 'failed'

    piper_cmd = [
        piper_bin,
        '--model', model_path,
        '--output_file', '-',
        '--length_scale', str(profile.length_scale),
        '--noise_scale', str(profile.noise_scale),
        '--noise_w', str(profile.noise_w),
    ]
    play_cmd = _aplay_command(output_device)
    piper_proc = subprocess.Popen(
        piper_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    assert piper_proc.stdin is not None
    piper_proc.stdin.write(text.encode('utf-8'))
    piper_proc.stdin.close()
    assert piper_proc.stdout is not None
    subprocess.run(play_cmd, stdin=piper_proc.stdout, check=False)
    piper_proc.wait(timeout=30)
    return 'spoken'


def _speak_espeak(text: str, output_device: str) -> str:
    """Fallback to espeak-ng when Piper is not installed."""
    espeak = shutil.which('espeak-ng') or shutil.which('espeak')
    if espeak is None:
        return 'logged'
    cmd = [espeak, '-s', '150', '-v', 'en-us', text]
    subprocess.run(cmd, check=False)
    return 'spoken'


def _aplay_command(output_device: str) -> list[str]:
    """Build an aplay command for optional ALSA device selection."""
    aplay = shutil.which('aplay') or 'aplay'
    if output_device:
        return [aplay, '-D', output_device]
    return [aplay]
