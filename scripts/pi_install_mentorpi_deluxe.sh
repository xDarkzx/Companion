#!/usr/bin/env bash
# One-shot Pi 5 setup for MentorPi Mailun/Ackermann Deluxe kit.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ">>> ROS 2 Jazzy"
bash "$ROOT/scripts/wsl_install_ros2.sh"

echo ">>> Nav2 + SLAM"
bash "$ROOT/scripts/pi_install_nav2.sh"

echo ">>> Voice (WonderEcho Pro + Whisper + espeak/Piper)"
bash "$ROOT/scripts/pi_install_voice.sh"
sudo apt-get install -y espeak-ng
pip3 install --user piper-tts 2>/dev/null || echo "WARN: piper-tts optional — use espeak-ng"

echo ">>> MentorPi vendor drivers"
bash "$ROOT/scripts/fetch_mentorpi_vendor.sh"

echo ">>> udev rules for depth camera (vendor)"
if [ -d "$ROOT/ros2_ws/src/vendor/peripherals/scripts" ]; then
  sudo cp "$ROOT/ros2_ws/src/vendor/peripherals/scripts/"*.rules /etc/udev/rules.d/ 2>/dev/null || true
  sudo udevadm control --reload-rules
fi

echo ">>> Build Companion stack"
cd "$ROOT/ros2_ws"
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
colcon test --packages-select companion_interfaces companion_brain companion_face \
  companion_memory companion_agent companion_behaviors companion_body \
  companion_perception companion_voice companion_bringup
colcon test-result --verbose

echo "DONE_OK — launch with:"
echo "  ros2 launch companion_bringup mentorpi_deluxe.launch.py"
