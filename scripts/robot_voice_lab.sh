#!/usr/bin/env bash
# Hear robot TTS profiles, pick one, generate the full phrase library.
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/assets/phrases"
PROFILE="${1:-}"
export COMPANION_ROOT="$ROOT"
export PULSE_SERVER="${PULSE_SERVER:-unix:/mnt/wslg/PulseServer}"

echo "=== Companion robot voice lab ==="
echo ""

if ! command -v espeak-ng >/dev/null 2>&1; then
  echo ">>> Installing espeak-ng (offline fallback)..."
  sudo apt-get update
  sudo apt-get install -y espeak-ng
fi

if ! command -v sox >/dev/null 2>&1; then
  echo ">>> Installing sox (robot polish)..."
  sudo apt-get install -y sox libsox-fmt-all
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo ">>> Installing ffmpeg..."
  sudo apt-get install -y ffmpeg
fi

echo ""
echo "Available profiles:"
python3 "$ROOT/tools/generate_robot_phrases.py" --list-profiles
echo ""

if [[ -z "$PROFILE" ]]; then
  echo "Step 1 — LISTEN to each voice (Enter between profiles, Ctrl+C when done):"
  echo "  bash scripts/robot_voice_lab.sh espeak_chibi   # skip preview, generate now"
  echo ""
  python3 "$ROOT/tools/preview_robot_tts.py" --all-lines || true
  echo ""
  read -r -p "Which profile key? [espeak_chibi]: " PROFILE
  PROFILE="${PROFILE:-espeak_chibi}"
fi

echo ""
echo "Step 2 — Download free robot beeps/boops (Kenney CC0)..."
bash "$ROOT/scripts/fetch_robot_sfx.sh" || true

echo ""
echo "Step 3 — Generating all spoken phrase WAVs with profile: $PROFILE"
python3 "$ROOT/tools/generate_robot_phrases.py" \
  --profile "$PROFILE" \
  --save-profile \
  --output "$OUT" \
  --play

mkdir -p "$ROOT/ros2_ws/src/companion_voice/assets/phrases"
cp -f "$OUT"/*.wav "$ROOT/ros2_ws/src/companion_voice/assets/phrases/" 2>/dev/null || true

if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  # shellcheck source=/dev/null
  source /opt/ros/jazzy/setup.bash
  cd "$ROOT/ros2_ws"
  colcon build --packages-select companion_voice companion_bringup
fi

echo ""
echo "Done. Launch: bash scripts/desktop_demo.sh whisper"
