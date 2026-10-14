#!/usr/bin/env bash
# Send one voice command to a running desktop prototype.
set -eo pipefail
CMD="${1:?usage: desktop_send_command.sh 'your command here'}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=/dev/null
source /opt/ros/jazzy/setup.bash
# shellcheck source=/dev/null
source "$ROOT/ros2_ws/install/setup.bash"
ros2 topic pub --once /companion/voice_command std_msgs/msg/String "{data: \"$CMD\"}"
