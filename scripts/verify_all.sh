#!/usr/bin/env bash
# Full quality gate: line limit, ruff, colcon build + test (Companion packages only).
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PACKAGES=(
  companion_interfaces
  companion_brain
  companion_face
  companion_memory
  companion_agent
  companion_behaviors
  companion_body
  companion_perception
  companion_voice
  companion_vision
  companion_bringup
)

echo ">>> 800-line guard (Companion packages only)"
for pkg in "${PACKAGES[@]}"; do
  if [ -d "ros2_ws/src/$pkg" ]; then
    python3 tools/check_file_length.py "ros2_ws/src/$pkg"
  fi
done
python3 tools/check_file_length.py tools

echo ">>> ruff (pinned in requirements-dev.txt)"
ruff check ros2_ws/src/companion_* tools

echo ">>> generated docs are current"
python3 tools/gen_architecture_diagram.py --check

echo ">>> tools pytest (architecture + test honesty gates)"
python3 -m pytest tools -q

echo ">>> colcon build + test (lint + behavioral integration)"
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select "${PACKAGES[@]}"
source install/setup.bash
colcon test --packages-select "${PACKAGES[@]}"
colcon test-result --verbose

echo "DONE_OK — all Companion gates passed"
