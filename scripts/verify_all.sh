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
  companion_bringup
)

echo ">>> 800-line guard (Companion packages only)"
for pkg in "${PACKAGES[@]}"; do
  if [ -d "ros2_ws/src/$pkg" ]; then
    python3 tools/check_file_length.py "ros2_ws/src/$pkg"
  fi
done
python3 tools/check_file_length.py tools

echo ">>> ruff"
if command -v ruff >/dev/null 2>&1; then
  ruff check ros2_ws/src/companion_* tools
else
  pip3 install --user ruff >/dev/null 2>&1 || pip install --user ruff
  ruff check ros2_ws/src/companion_* tools
fi

echo ">>> tools pytest (architecture + test honesty gates)"
python3 -m pytest tools/test_check_file_length.py tools/test_companion_architecture.py tools/test_suite_honesty.py -q

echo ">>> colcon build + test (lint + behavioral integration)"
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select "${PACKAGES[@]}"
source install/setup.bash
colcon test --packages-select "${PACKAGES[@]}"
colcon test-result --verbose

echo "DONE_OK — all Companion gates passed"
