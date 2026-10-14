# Deploy Companion on MentorPi A1 (Ackermann)

Step-by-step for **Raspberry Pi 5 smart car MentorPi Mailun/Ackerman** with the **enterprise stack**
(Ubuntu 24.04 + Jazzy + Nav2 + vendor drivers + Companion).

Official Hiwonder docs: https://docs.hiwonder.com/projects/MentorPi/en/latest/

---

## 1. Before the robot arrives (do now on WSL2)

```bash
# ROS 2 Jazzy (once)
bash scripts/wsl_install_ros2.sh
source /opt/ros/jazzy/setup.bash

# Nav2 + SLAM (optional in WSL until hardware)
bash scripts/pi_install_nav2.sh

# Voice (when USB mic/speaker arrives — optional in WSL)
bash scripts/pi_install_mentorpi_deluxe.sh   # all-in-one Pi setup
bash scripts/pi_install_voice.sh

# MentorPi driver packages (Jazzy port)
bash scripts/fetch_mentorpi_vendor.sh

cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
colcon test && colcon test-result --verbose

# Run software stack without hardware
ros2 launch companion_bringup companion_stack.launch.py
```

---

## 2. When the robot arrives — stock SD first

| Step | Action |
|------|--------|
| 1 | Power on, connect to WiFi `HW*` / password `hiwonder` |
| 2 | VNC to `192.168.149.1` — user `pi`, password `raspberrypi` |
| 3 | Config tool → **MentorPi_Acker** + your camera type → Save → Apply |
| 4 | Run vendor demos (teleop, lidar, camera) |
| 5 | **Clone SD card** to backup `.img` (Win32 Disk Imager / `dd`) |
| 6 | Email **support@hiwonder.com** + order number → official image + source |

Do **not** wipe the card until backup + source are secured.

---

## 3. Flash Companion OS (second SD card recommended)

Use **Raspberry Pi Imager**:

- OS: **Ubuntu Server 24.04 LTS (64-bit)**
- Enable SSH, set user + WiFi

On the Pi:

```bash
bash scripts/wsl_install_ros2.sh    # same script as WSL
bash scripts/pi_install_nav2.sh
git clone <your-repo> companion && cd companion
bash scripts/fetch_mentorpi_vendor.sh
cd ros2_ws && colcon build && source install/setup.bash
```

---

## 4. Hardware bringup

```bash
# Low-level drivers + lidar + camera (when vendor fetch complete)
ros2 launch companion_bringup mentorpi_body.launch.py

# Companion brain + agent + face
ros2 launch companion_bringup companion_stack.launch.py

# Test command routing
ros2 topic pub /companion/voice_command std_msgs/msg/String \
  "{data: 'patrol the home'}" --once
```

Verify vendor topics:

```bash
ros2 topic list | grep -E 'cmd_vel|scan|odom|camera'
ros2 topic echo /companion/body_status
```

---

## 5. Mapping + patrol (Nav2)

1. Teleop drive slowly around the house — build map with `slam_toolbox`
2. Save map to `ros2_ws/src/companion_bringup/maps/home.yaml`
3. Edit `config/waypoints.yaml` with patrol points
4. Launch Nav2 + waypoint follower (wired in Phase 3 `companion_body`)

Nav2 tutorial: https://docs.nav2.org/

---

## 6. Voice + AI (Phase 3)

See **`docs/HUMAN_INTERFACE.md`** for commands, memory, and patrol animations.
See **`docs/VISION_AND_HAILO.md`** for the Hailo hat + YOLO pipeline.

| Component | Install |
|-----------|---------|
| STT | Whisper (local) |
| Agent | `pip install jpl-rosa` — NASA ROSA on Jazzy |
| LLM | Ollama on Pi 5 or cloud API |
| Detection | YOLO + Hailo hat |

ROSA custom tools call the same `/companion/behavior_request` topic as `companion_agent`.

---

## 7. Ackermann notes

- Steering servos: run Hiwonder `Servo.sh` calibration on stock SD before reflash, save offsets
- Chassis param: `MentorPi_Acker` in vendor launch YAML
- Max speed for "play with dog" mode: cap in `companion_behaviors` params (Phase 3)

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `vendor_missing` on `/companion/body_status` | Run `fetch_mentorpi_vendor.sh`, rebuild |
| colcon skips vendor | Remove `vendor/COLCON_IGNORE` after fetch |
| Driver build fails | `rosdep install --from-paths src/vendor -y` |
| Official vs community drivers | Prefer Hiwonder email source when available |
