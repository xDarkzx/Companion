#!/usr/bin/env bash
# Generate the full robot phrase library from a TTS profile (hear first in robot_voice_lab.sh).
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${COMPANION_TTS_PROFILE:-}"
export COMPANION_ROOT="$ROOT"
export PULSE_SERVER="${PULSE_SERVER:-unix:/mnt/wslg/PulseServer}"

if [[ -n "$PROFILE" ]]; then
  exec bash "$ROOT/scripts/robot_voice_lab.sh" "$PROFILE"
fi

echo ">>> Use the voice lab to hear profiles and generate clips:"
echo "    bash scripts/robot_voice_lab.sh"
echo ""
echo "Or generate with a profile directly:"
echo "    bash scripts/robot_voice_lab.sh espeak_chibi"
exit 0
