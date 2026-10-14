# Setup

There are three ways in, depending on what you want to do.

| Goal | Needs | Time |
|---|---|---|
| Run every test exactly as CI does | Docker | One command, about 5 minutes the first time |
| Develop the ROS stack | Ubuntu 24.04 (native, WSL2 or a Pi 5) with ROS 2 Jazzy | About 30 minutes |
| Run the vision models, benchmarks or webcam demo | Python 3.10+ and a CUDA GPU (a CPU works, slowly) | About 10 minutes plus model downloads |

## 1. Run the full gate in Docker

```bash
bash scripts/docker_verify.sh
```

This builds `docker/ci.Dockerfile` (ROS 2 Jazzy plus every dependency the packages declare),
copies the repository into the container read-only, and runs `scripts/verify_all.sh`:

- the line guard;
- ruff;
- the architecture and test-honesty validators;
- `colcon build`;
- `colcon test` (lint, unit and launch tests).

It ends with `DONE_OK` when everything passes.

## 2. Develop the ROS stack (Ubuntu 24.04)

On Windows, install Ubuntu first with `wsl --install -d Ubuntu-24.04`. On a Pi 5, flash
Ubuntu Server 24.04 (64-bit) with Raspberry Pi Imager. Then install ROS 2 Jazzy following the
[official guide](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
(`ros-jazzy-ros-base` and `ros-dev-tools`), and build:

```bash
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
colcon test && colcon test-result --verbose
```

Run something:

```bash
ros2 launch companion_bringup desktop_dev.launch.py     # face window + keyboard commands + memory
bash scripts/desktop_demo.sh keyboard true              # the same, with a USB camera and perception
ros2 topic pub --once /companion/voice_command std_msgs/String "{data: 'where is the mug'}"
```

`desktop_dev.launch.py` opens the face in a window (WSLg on Windows) and reads commands typed
at the `Companion>` prompt. With `voice_mode:=whisper` it listens to the default microphone
instead.

## 3. Vision models, benchmarks and the webcam demo

```bash
python -m venv .venv-vision && . .venv-vision/bin/activate     # Windows: .venv-vision\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cu128   # or /cpu
pip install -e "ros2_ws/src/companion_vision[models,demo]" pytest pycocotools h5py scipy
export HF_HOME=/path/with/space/hf-cache                           # models are a few GB

COMPANION_MODEL_TESTS=1 pytest ros2_ws/src/companion_vision/test   # real-model smoke tests
python -m companion_vision.demo --query mug --query "water bottle"
```

Benchmarks are described in [EVALUATION.md](EVALUATION.md).

## Tooling

- **pre-commit:** `pip install pre-commit && pre-commit install` runs ruff, the line guard, a
  secret scan and commit-message checks on every commit.
- **ruff:** pinned in `requirements-dev.txt`, so local and CI results match.
- **Regenerated documents:** `python tools/gen_architecture_diagram.py` and
  `python eval/report.py` rebuild the generated parts of the docs. CI checks both are current.
