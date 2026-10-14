# MentorPi Mailun/Ackermann Deluxe — Pi 5 Stack

Full Companion integration for the **Raspberry Pi 5 smart car MentorPi Mailun/Ackerman AI large model vision ROS2 robot deluxe** kit:

- **HD depth camera** (ascamera vendor stack)
- **WonderEcho Pro voice box** (USB mic + speaker)
- **Ackermann chassis** + lidar (vendor orchestrator)
- **Companion** personality, memory, voice commands, patrol face

Related: [DEPLOY_MENTORPI.md](DEPLOY_MENTORPI.md) · [VOICE_HARDWARE.md](VOICE_HARDWARE.md) · [ENTERPRISE_STACK.md](ENTERPRISE_STACK.md)

---

## Architecture

```
WonderEcho USB ──► stt_node (Whisper) ──► agent_node ──► behaviors ──► face
HD depth cam   ──► camera_watch_node ──► /companion/camera_status
Agent plans    ──► nav_bridge_node ──► Nav2 action ──► vendor cmd_vel
Vendor stack   ──► lidar / odom / motors (mentorpi_body.launch.py)
```

All Companion logic lives in modular `companion_*` packages (≤800 lines per file).

---

## One-command Pi setup

```bash
bash scripts/pi_install_mentorpi_deluxe.sh
```

Then on every boot:

```bash
cd ~/companion/ros2_ws && source install/setup.bash
ros2 launch companion_bringup mentorpi_deluxe.launch.py
```

---

## Launch options

| Launch file | Use |
|-------------|-----|
| `mentorpi_deluxe.launch.py` | **Production** — body + voice + camera + agent |
| `companion_stack.launch.py` | Dev/WSL — software only, simulated nav |
| `mentorpi_body.launch.py` | Vendor drivers only |

```bash
# Headless Pi (no pygame window)
ros2 launch companion_bringup mentorpi_deluxe.launch.py show_face:=false

# Skip vendor if testing brain only
ros2 launch companion_bringup mentorpi_deluxe.launch.py enable_body:=false
```

---

## Config files

| File | Purpose |
|------|---------|
| `config/mentorpi_deluxe.yaml` | Pi defaults: whisper, espeak, Nav2 action, camera topics |
| `config/places.yaml` | Named map goals (kitchen, dock, …) |
| `config/voice.yaml` | Dev keyboard mode |
| `config/stack.yaml` | WSL dev (simulated nav 4 s) |

### After first SLAM session

1. Drive the robot around with teleop + `slam_toolbox`
2. Save map
3. Edit `places.yaml` with real x/y/yaw from RViz Nav2 goals

### Voice box ALSA device

```bash
arecord -l && aplay -l
```

Set `input_device` / `output_device` in `mentorpi_deluxe.yaml` (e.g. `plughw:2,0`).

---

## Camera topics (vendor)

| Stream | Topic |
|--------|-------|
| RGB | `/ascamera/camera_publisher/rgb0/image` |
| Depth | `/ascamera/camera_publisher/depth0/image_raw` |
| Status | `/companion/camera_status` (`ready`, `waiting`, `stale`, …) |

`camera_watch_node` monitors frame freshness — `detector_node` runs YOLO CPU or idle stub until Hailo.

---

## Navigation

On Pi, `nav_bridge_node` uses **Nav2 `navigate_to_pose` action** (`use_nav_action: true`, `simulated_travel_sec: 0`).

In WSL dev, `stack.yaml` uses **simulated arrival** (4 s timer) and `/goal_pose` fallback.

Multi-step commands wait for `/companion/nav_status: arrived` before step 2:

```bash
ros2 topic pub /companion/voice_command std_msgs/msg/String \
  "{data: 'go to kitchen and patrol'}" --once
```

---

## Quality gate (run before every merge)

```bash
bash scripts/verify_all.sh
```

Checks:

1. **800-line guard** per Companion package
2. **ruff** lint on all `companion_*` sources
3. **colcon build + test** (flake8, pep257, unit, integration)

---

## Modular package map

| Package | Modules | Role |
|---------|---------|------|
| `companion_voice` | `stt_node`, `tts_node`, `whisper_capture`, `piper_player` | USB voice |
| `companion_perception` | `camera_watch_node`, `detector_node` | Depth cam health + YOLO detections |
| `companion_body` | `nav_bridge_node`, `nav_action_client`, `goal_pose_builder` | Nav2 bridge |
| `companion_agent` | `agent_node`, `parse_command` | Voice → plans |
| `companion_behaviors` | `behavior_controller_node`, `patrol_animator` | Face emotions |
| `companion_memory` | `places_store`, `rag_retriever` | Named places |
| `companion_face` | `face_ascii_node`, `ascii_renderer` | ASCII face + cloud badge |
| `companion_bringup` | launches + YAML | Wiring |

Vendor code stays in `ros2_ws/src/vendor/` (fetched, not committed).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `camera_status: waiting` | Run `mentorpi_body.launch.py`; check `ros2 topic list \| grep ascamera` |
| No voice | `bash scripts/pi_install_voice.sh`; set ALSA device in YAML |
| Nav never arrives | Ensure Nav2 running; check `ros2 action list \| grep navigate` |
| `vendor_missing` | `bash scripts/fetch_mentorpi_vendor.sh` + rebuild |

---

## Phase 3 (not blocking deluxe bringup)

- YOLO + Hailo person/dog detection
- NASA ROSA free-form speech
- Vector RAG + LLM tool loop
- GPIO LCD face (drop pygame on Pi)
