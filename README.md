# Companion 🤖💚

An **emotion-aware AI robot companion**. It shows feelings on an animated face, and
— the differentiator — it senses when *you* are upset, sad, or need cheering up, and
responds with empathy.

The **Raspberry Pi 5 is always the brain** (ROS 2 + AI + face + empathy logic). The
**body is swappable** — currently a **Freenove Robot Dog Kit** (Pi-driven) — it's just
another node that plugs into the same backbone.

## Status

**Phase 2 — Emotional Face + human interface.** See [`docs/PROGRESS.md`](docs/PROGRESS.md) for live
status and [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full plan.

**Key docs:** [`DESKTOP_DEV.md`](docs/DESKTOP_DEV.md) · [`MENTORPI_DELUXE.md`](docs/MENTORPI_DELUXE.md) · [`HUMAN_INTERFACE.md`](docs/HUMAN_INTERFACE.md) · [`VOICE_HARDWARE.md`](docs/VOICE_HARDWARE.md) · [`ENTERPRISE_STACK.md`](docs/ENTERPRISE_STACK.md)

## Tech stack

- **ROS 2 Jazzy Jalisco** on **Ubuntu 24.04** (ROS 1 is EOL — not used).
- **Python (`rclpy`)** by default.
- **Dev:** WSL2 (Ubuntu 24.04) for local dev + tests → deploy to the Pi for hardware.

## Repository layout

```
Companion/
├─ CLAUDE.md                 ← project rules (read this first)
├─ docs/                     ← roadmap, progress, design specs
├─ ros2_ws/src/              ← ROS 2 packages
│  ├─ companion_interfaces/ ← message contracts
│  ├─ companion_bringup/    ← launch files + config (places.yaml)
│  ├─ companion_agent/      ← voice/text → multi-step commands
│  ├─ companion_memory/     ← named places + people
│  ├─ companion_behaviors/  ← patrol animations, behavior → emotion
│  ├─ companion_body/       ← nav_bridge → Nav2, vendor status
│  ├─ companion_voice/      ← STT/TTS USB audio (Whisper)
│  ├─ companion_perception/ ← vision stub (Hailo Phase 3)
│  ├─ companion_brain/      ← personality/empathy
│  ├─ companion_face/       ← face renderer
│  └─ vendor/               ← MentorPi drivers (fetched, not committed)
└─ tools/                    ← helper scripts (e.g. 800-line guard)
```

## Setup & quickstart

Full step-by-step install for **WSL2** and the **Pi** is in
[`docs/SETUP.md`](docs/SETUP.md). Once ROS 2 Jazzy is installed:

```bash
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
colcon test && colcon test-result --verbose   # lint + unit + integration
ros2 launch companion_bringup desktop_dev.launch.py          # PC prototype (face + memory)
bash scripts/desktop_demo.sh                                 # same, one command from repo root
ros2 launch companion_bringup companion_stack.launch.py   # dev / WSL
ros2 launch companion_bringup mentorpi_deluxe.launch.py   # Pi 5 + MentorPi deluxe
ros2 launch companion_bringup demo_face.launch.py          # face + voice personality demo
```

> **Note:** ROS 2 runs on **Linux only** — build/run these in WSL2 or on the Pi, not in
> native Windows. The 800-line guard (`python tools/check_file_length.py .`) runs anywhere.

## Rules

All contributors (human or AI) follow [`CLAUDE.md`](CLAUDE.md): small modular files
(≤800 lines), typed message contracts, TDD, clean shutdown, no magic numbers.
