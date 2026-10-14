#!/usr/bin/env bash
# Install Nav2 + SLAM + exploration stack on Ubuntu 24.04 / ROS 2 Jazzy (Pi or WSL2).
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo ">>> Nav2 + SLAM + tools"
sudo apt-get update -y
sudo apt-get install -y \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-nav2-waypoint-follower \
  ros-jazzy-robot-localization

echo ">>> m-explore-ros2 (optional autonomous wander)"
EXPLORE_DIR="${HOME}/ros2_ws/src/m-explore-ros2"
if [[ ! -d "${EXPLORE_DIR}" ]]; then
  git clone --depth 1 https://github.com/robo-friends/m-explore-ros2.git "${EXPLORE_DIR}"
fi

echo "DONE_OK — source /opt/ros/jazzy/setup.bash then colcon build m-explore if cloned"
