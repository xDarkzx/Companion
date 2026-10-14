# Hardware

Companion's brain runs on a **Raspberry Pi 5** or a desktop. The body is swappable. The
code targets the **Hiwonder MentorPi** (Pi 5, four-wheel base, lidar, RGB-D camera, USB
voice box) as its reference body, and the MentorPi launch files and topic names are
included.

## What has been run where

| Environment | What runs | How it is checked |
|---|---|---|
| Docker (`ros:jazzy-ros-base`), every pull request | The whole ROS stack: build, lint, unit and launch tests, architecture validators | `bash scripts/docker_verify.sh`, and the `ros` CI job |
| Desktop GPU (RTX 5070, Windows) | `companion_vision` with real models: benchmarks, webcam demo, model smoke tests | `eval/` result files, `COMPANION_MODEL_TESTS=1 pytest` |

The launch files below are the deployment path to the MentorPi. They are built and
launch-tested in Docker on every pull request. Running them on the robot is the next
milestone on the [roadmap](ROADMAP.md).

## Reference body: MentorPi

| Part | Role in Companion | ROS interface |
|---|---|---|
| Raspberry Pi 5 | Runs every Companion node | — |
| RGB-D camera (`ascamera`) | Perception: RGB, depth and intrinsics | `/ascamera/camera_publisher/rgb0/image`, `depth0/image_raw`, `rgb0/camera_info` |
| Lidar + wheel odometry | Mapping and navigation | Vendor drivers into Nav2 and `slam_toolbox` |
| USB voice box (mic + speaker) | Speech in and out | ALSA device in `config/mentorpi_deluxe.yaml` |
| Base controller | Drives the wheels | Nav2 `cmd_vel`; Companion never publishes motor commands |

Vendor drivers are fetched, not committed: `bash scripts/fetch_mentorpi_vendor.sh`.

### Install and launch on the Pi

```bash
bash scripts/pi_install_mentorpi_deluxe.sh   # ROS 2 Jazzy, Nav2, voice, vendor drivers
bash scripts/pi_install_perception.sh        # CPU PyTorch and the vision models
cd ros2_ws && colcon build && source install/setup.bash
ros2 launch companion_bringup mentorpi_deluxe.launch.py               # body, voice, camera, agent, face
ros2 launch companion_bringup mentorpi_deluxe.launch.py show_face:=false   # headless
```

After the first mapping session, drive with teleop and `slam_toolbox`, save the map, and put
real coordinates for each room into `config/places.yaml`.

### Perception on the Pi

The Pi 5 has no GPU, so perception runs on the CPU. To keep the robot responsive:

- the watch list (`watch_labels`) runs at `watch_rate_hz`, which defaults to 2 Hz and should be
  lowered on the Pi;
- `FindObject` runs only when someone asks;
- `depth_mode: sensor` uses the camera's depth and skips the monocular model entirely.

A Hailo-8 accelerator (AI HAT+) would offload detection. That needs models compiled for Hailo
and is on the [roadmap](ROADMAP.md).

## Voice hardware

Any USB microphone and speaker work through ALSA. Speech to text is Whisper (`faster-whisper`,
`base.en` by default) or a keyboard prompt for development. Text to speech is Piper (neural,
offline) or espeak-ng. Find the devices with `arecord -l` and `aplay -l`, then set them in the
voice section of the config. Only local, open-source speech engines are used.

## Desktop with a webcam

A webcam has no depth sensor, so the desktop configuration (`config/desktop_vision.yaml`) uses
monocular depth. Monocular distances are approximate: see the measured error and scale bias in
[EVALUATION.md](EVALUATION.md).

```bash
bash scripts/desktop_demo.sh keyboard true   # WSL2: face window, keyboard commands, USB camera
python -m companion_vision.demo --query mug   # any OS with a GPU: live detection overlay
```
