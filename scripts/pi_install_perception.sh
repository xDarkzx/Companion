#!/usr/bin/env bash
# Install the vision model stack for grounded_detector_node on a CPU-only machine (Pi 5).
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ">>> CPU PyTorch + transformers for OWLv2 / Grounding DINO / Depth Anything"
pip3 install --user --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu
pip3 install --user --break-system-packages -e "$ROOT/ros2_ws/src/companion_vision[models]"

echo "DONE_OK — choose backend and depth_mode in companion_bringup/config/perception.yaml"
