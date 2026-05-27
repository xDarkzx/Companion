#!/usr/bin/env bash
# Install ROS 2 Jazzy + dev tools on Ubuntu 24.04 (WSL2 or Pi).
# Idempotent-ish: safe to re-run. Logs to /tmp/ros_install.log.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo ">>> apt update + base tools"
sudo apt-get update -y
sudo apt-get install -y locales software-properties-common curl gnupg

echo ">>> locale"
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

echo ">>> universe repo"
sudo add-apt-repository -y universe

echo ">>> ROS 2 apt source"
RVER=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
  | grep -oP '"tag_name":\s*"\K[^"]+')
echo "    ros-apt-source version: ${RVER}"
CODENAME=$(. /etc/os-release && echo "${UBUNTU_CODENAME:-${VERSION_CODENAME}}")
curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${RVER}/ros2-apt-source_${RVER}.${CODENAME}_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

echo ">>> install ros-jazzy-ros-base + dev tools"
sudo apt-get update -y
sudo apt-get install -y \
  ros-jazzy-ros-base \
  ros-dev-tools \
  python3-colcon-common-extensions \
  ros-jazzy-launch-testing \
  ros-jazzy-launch-testing-ros

echo ">>> rosdep init/update"
sudo rosdep init 2>/dev/null || true
rosdep update

echo "DONE_OK"
