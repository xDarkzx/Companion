#!/usr/bin/env bash
# One-time PC/WSL dependencies for the Companion desktop prototype.
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WITH_VISION="${1:-false}"

# shellcheck source=/dev/null
source "$ROOT/scripts/mic_deps.sh"

echo "=== Companion desktop dependencies ==="

sudo apt-get update
sudo apt-get install -y \
  espeak-ng \
  python3-pygame \
  python3-pip \
  pulseaudio-utils \
  alsa-utils

mic_apt_audio_libs

if [[ "$WITH_VISION" == "true" ]]; then
  if ! command -v ros2 >/dev/null 2>&1; then
    echo "ROS 2 not sourced. Run: bash scripts/wsl_install_ros2.sh first"
    exit 1
  fi
  # shellcheck source=/dev/null
  source /opt/ros/jazzy/setup.bash
  sudo apt-get install -y ros-jazzy-usb-cam
fi

mic_deps_install

touch "$ROOT/.desktop_deps_ok"

if [[ "$WITH_VISION" == "true" ]]; then
  python3 -m pip install --break-system-packages ultralytics opencv-python-headless
  echo ""
  echo "Optional: bash scripts/desktop_download_yolo.sh"
fi

echo ""
echo "Done. Launch with: bash scripts/desktop_demo.sh"
