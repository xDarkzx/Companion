# Setup — ROS 2 Jazzy for Companion

Two environments, **same code**:

- **WSL2 (Ubuntu 24.04) on your Windows PC** — daily development + automated tests.
- **Raspberry Pi 5 (Ubuntu Server 24.04)** — hardware testing + deployment.

The ROS 2 install steps are **identical** on both. Commands below are verified against
the official ROS 2 Jazzy docs:
<https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html>

---

## Part A — Install WSL2 (Windows only, one time)

In **Windows PowerShell (as Administrator)**:

```powershell
wsl --install -d Ubuntu-24.04
```

Reboot if prompted, then launch **Ubuntu 24.04** from the Start menu and create your
Linux username/password. You now have an Ubuntu terminal — use it for everything below.

## Part B — Flash the Pi (Pi only, one time)

1. Install **Raspberry Pi Imager** on Windows.
2. Choose OS → **Other general-purpose OS → Ubuntu → Ubuntu Server 24.04 LTS (64-bit)**.
3. Set hostname, enable SSH, set username/Wi-Fi in the Imager settings, write the card.
4. Boot the Pi, then SSH in from Windows: `ssh <user>@<pi-hostname>.local`.

---

## Part C — Install ROS 2 Jazzy (both WSL2 and Pi, identical)

```bash
# 1. Locale (UTF-8)
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 2. Enable the universe repository
sudo apt install -y software-properties-common
sudo add-apt-repository universe

# 3. Add the ROS 2 apt source (official method)
sudo apt update && sudo apt install -y curl
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

# 4. Install ROS 2 base + dev tools
sudo apt update && sudo apt upgrade -y
sudo apt install -y ros-jazzy-ros-base ros-dev-tools

# 5. Source ROS in every new shell (add to ~/.bashrc so it is automatic)
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## Part D — Get the code + build + test + run

```bash
# Clone into the Linux filesystem (faster than /mnt/d). Use your repo URL/path.
git clone <your-repo-url> companion && cd companion/ros2_ws

# Resolve package dependencies declared in the package.xml files
sudo rosdep init   # first time only; ignore "already exists" errors
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# Build
colcon build

# Source this workspace's overlay (every new shell, after sourcing ROS itself)
source install/setup.bash

# Run the test suite (lint + unit + integration)
colcon test && colcon test-result --verbose

# Run the Phase 1 demo
ros2 launch companion_bringup demo.launch.py
```

**Expected demo output** — the brain publishing and the face logging, ~1/second:

```
[heartbeat_node]: Published emotion: neutral (0.8)
[face_stub_node]: Showing emotion: neutral (0.80) from brain
[heartbeat_node]: Published emotion: happy (0.8)
[face_stub_node]: Showing emotion: happy (0.80) from brain
...
```

Press `Ctrl+C` to stop. Inspect the topic live with:
`ros2 topic echo /companion/robot_emotion`.

---

## The 800-line guard (any OS, including Windows)

```bash
python tools/check_file_length.py .
```

Exits non-zero and lists offenders if any source file exceeds 800 lines.
