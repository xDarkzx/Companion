#!/usr/bin/env bash
# Test microphone + Whisper STT before launching the full demo.
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="$ROOT/ros2_ws"

# shellcheck source=/dev/null
source "$ROOT/scripts/mic_deps.sh"

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  # shellcheck source=/dev/null
  source /opt/ros/jazzy/setup.bash
fi
if [[ -f "$WS/install/setup.bash" ]]; then
  # shellcheck source=/dev/null
  source "$WS/install/setup.bash"
fi

echo "=== Companion mic test ==="
export PULSE_SERVER="${PULSE_SERVER:-unix:/mnt/wslg/PulseServer}"

if ! mic_deps_import_ok; then
  mic_deps_install
fi

python3 <<'PY'
import sys
try:
    import sounddevice as sd
except ImportError:
    print("FAIL: sounddevice not installed. Run: bash scripts/desktop_install_deps.sh")
    sys.exit(1)

from companion_voice.whisper_capture import (
    log_input_devices,
    resolve_input_device_index,
    use_pulse_capture,
)
from companion_voice.wslg_audio import pulse_env, record_chunk_pulse

device_index = resolve_input_device_index("")
pulse_mic = use_pulse_capture() and device_index is None
print("\n--- Input devices ---")
log_input_devices(print, active_index=device_index)
if device_index is None and not pulse_mic:
    print("\nFAIL: No microphone input device found.")
    print("  - Windows: Settings > Privacy > Microphone > allow for WSL/desktop")
    sys.exit(1)

print("\nRecording 3 seconds — speak now...")
if pulse_mic:
    print("Using WSLg mic (parecord)")
    audio = record_chunk_pulse(3.0, 16000)
else:
    print(f"Using device index: {device_index}")
    audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype="float32", device=device_index)
    sd.wait()
    audio = np.asarray(audio, dtype=np.float32).flatten().tolist()
import numpy as np
rms = float(np.sqrt(np.mean(np.square(np.asarray(audio, dtype=np.float32)))))
print(f"Audio level (RMS): {rms:.4f}")
if rms < 0.008:
    print("\nFAIL: Very quiet — mic not picking up speech.")
    print("  - Set stt_node.input_device to a different index in desktop_dev.yaml")
    sys.exit(1)

print("Mic level OK.")
PY

echo ""
echo ">>> Whisper transcribe test (speak when prompted)..."
python3 <<'PY'
from faster_whisper import WhisperModel
import numpy as np
import sounddevice as sd
from companion_voice.whisper_capture import resolve_input_device_index, use_pulse_capture
from companion_voice.wslg_audio import record_chunk_pulse
import sounddevice as sd

device_index = resolve_input_device_index("")
pulse_mic = use_pulse_capture() and device_index is None
if device_index is None and not pulse_mic:
    raise SystemExit("No mic device")

print("Recording 4 seconds — speak now...")
if pulse_mic:
    samples = np.asarray(record_chunk_pulse(4.0, 16000), dtype=np.float32)
else:
    print(f"Device {device_index}")
    audio = sd.rec(int(4 * 16000), samplerate=16000, channels=1, dtype="float32", device=device_index)
    sd.wait()
    samples = np.asarray(audio, dtype=np.float32).flatten()
model = WhisperModel("base.en", device="cpu", compute_type="int8")
segments, _ = model.transcribe(samples, language="en", vad_filter=True)
text = " ".join(s.text.strip() for s in segments).strip()
print(f"Heard: {text!r}")
if not text:
    print("FAIL: Whisper heard silence — check mic device index.")
    raise SystemExit(1)
print("PASS: mic + Whisper working.")
PY

echo ""
echo "Launch: bash scripts/desktop_demo.sh"
