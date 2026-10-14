# MentorPi vendor drivers (Hiwonder hardware)

Third-party ROS 2 packages for **RRC Lite motors, lidar, camera, IMU**.
Not part of Companion — fetched separately so we never fork vendor code into `companion_*`.

## Fetch (before robot arrives)

From repo root on **WSL2 or Pi**:

```bash
bash scripts/fetch_mentorpi_vendor.sh
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
```

This copies packages from [MentorPi_ris](https://github.com/LinusGro/MentorPi_ris)
(Jazzy + Ubuntu 24.04) into `ros2_ws/src/vendor/`:

| Package | Role |
|---------|------|
| `driver` | RRC Lite — wheels, servos, IMU, buzzer |
| `peripherals` | Lidar + camera launch configs |
| `orchestrator_launch` | Brings up driver + sensors |
| `ldrobot-lidar-ros2` | STL-19P lidar |
| `simulations` | URDF |
| `calibration` / `imu_calib` | Sensor calibration |

## Official Hiwonder image (when robot ships)

1. **Boot stock SD once** — confirm hardware, then **clone the card** to a backup `.img`.
2. Email **support@hiwonder.com** with your **order number** for the official image + source.
3. Compare official `driver/` with this vendor copy; prefer official if newer.

Stock card uses **Pi OS + Docker + Humble**. Companion uses **Ubuntu 24.04 + Jazzy native**
— do not run both on one SD card.

## Ackermann A1 config

On stock SD (before reflash): desktop tool → **Machine Type → MentorPi_Acker**.

On Jazzy native: set chassis params in vendor launch YAML (see Hiwonder docs).

## COLCON_IGNORE

If `vendor/COLCON_IGNORE` exists, colcon skips unfetched vendor packages.
The fetch script removes it when packages are installed.
