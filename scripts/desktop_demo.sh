#!/usr/bin/env bash
# Launch the Companion PC prototype (face + mic + robot phrase TTS + memory).
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="$ROOT/ros2_ws"
VOICE_MODE="${1:-whisper}"
ENABLE_VISION="${2:-false}"
MODEL_PATH="${3:-}"
export COMPANION_ROOT="$ROOT"
# WSLg routes mic + speakers through PulseAudio (PortAudio often sees nothing).
export PULSE_SERVER="${PULSE_SERVER:-unix:/mnt/wslg/PulseServer}"

PHRASE_DIR="$ROOT/assets/phrases"

# shellcheck source=/dev/null
source "$ROOT/scripts/mic_deps.sh"

echo "=== Companion PC prototype ==="
echo "  voice:   $VOICE_MODE  (whisper = mic | keyboard = type)"
echo "  tts:     anime robot phrases (English clips)"
echo "  vision:  $ENABLE_VISION"
echo ""

if [[ ! -f "$ROOT/.desktop_deps_ok" ]]; then
  echo ">>> First run: bash scripts/desktop_install_deps.sh"
  echo ""
fi

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  # shellcheck source=/dev/null
  source /opt/ros/jazzy/setup.bash
fi

if ! command -v ros2 >/dev/null 2>&1; then
  echo "ROS 2 not found. Run: bash scripts/wsl_install_ros2.sh"
  exit 1
fi

if [[ ! -f "$WS/install/setup.bash" ]]; then
  echo ">>> First run: building workspace..."
  cd "$WS"
  colcon build --packages-select \
    companion_interfaces companion_memory companion_agent \
    companion_behaviors companion_body companion_brain \
    companion_face companion_perception companion_voice companion_bringup
fi

# shellcheck source=/dev/null
source "$WS/install/setup.bash"

if [[ ! -d "$PHRASE_DIR" ]] || [[ "$(find "$PHRASE_DIR" -maxdepth 1 -name '*.wav' 2>/dev/null | wc -l)" -lt 5 ]]; then
  echo ">>> Building robot phrase library (TTS profiles — hear & pick)..."
  bash "$ROOT/scripts/robot_voice_lab.sh" "${COMPANION_TTS_PROFILE:-espeak_chibi}"

# Piper optional fallback (phrase clips are primary).
export PATH="$ROOT/models/piper/piper:$PATH"

if [[ "$VOICE_MODE" == "whisper" ]]; then
  if ! mic_deps_import_ok; then
    echo ">>> Installing mic/STT deps (required for voice)..."
    mic_deps_install || bash "$ROOT/scripts/desktop_install_deps.sh"
  fi
  if ! mic_deps_import_ok; then
    echo "ERROR: Mic deps missing after install."
    echo "Try: bash scripts/desktop_mic_test.sh"
    python3 -c "import faster_whisper, sounddevice" 2>&1 || true
    exit 1
  fi
fi

if [[ "$ENABLE_VISION" == "true" ]]; then
  if ! ros2 pkg prefix usb_cam >/dev/null 2>&1; then
    echo ">>> Installing USB camera driver (one time)..."
    sudo apt-get update
    sudo apt-get install -y ros-jazzy-usb-cam
  fi
  if [[ -n "$MODEL_PATH" ]] && ! python3 -c "import ultralytics" 2>/dev/null; then
    echo ">>> Installing YOLO deps (one time)..."
    pip3 install --break-system-packages ultralytics
  fi
fi

echo ""
python3 -c "
from companion_voice.tts_engine import describe_tts
print('TTS engine:', describe_tts('${PHRASE_DIR}'))
" 2>/dev/null || echo "TTS engine: robot phrases"
echo ""
if [[ "$VOICE_MODE" == "whisper" ]]; then
  echo "Speak to Companion (Windows default mic via WSLg). Example phrases:"
else
  echo "Type at the Companion> prompt. Example phrases:"
fi
echo "  remember that my favorite color is blue"
echo "  what is my favorite color"
echo "  go to kitchen"
echo "  patrol the home"
echo "  stop"
echo ""
echo "Two windows: ASCII face (emotions) + optional vision preview."
echo "Press Esc in a window or Ctrl+C here to quit."
echo ""

LAUNCH_ARGS=(voice_mode:="$VOICE_MODE" enable_vision:="$ENABLE_VISION")

if [[ -n "$MODEL_PATH" ]]; then
  LAUNCH_ARGS+=(model_path:="$MODEL_PATH")
fi

cd "$WS"
exec ros2 launch companion_bringup desktop_dev.launch.py "${LAUNCH_ARGS[@]}"
