# Companion 🤖💚

An **emotion-aware AI robot companion**. It shows feelings on an animated face, and
— the differentiator — it senses when *you* are upset, sad, or need cheering up, and
responds with empathy.

The **Raspberry Pi 5 is always the brain** (ROS 2 + AI + face + empathy logic). The
**body is swappable** — currently a **Freenove Robot Dog Kit** (Pi-driven) — it's just
another node that plugs into the same backbone.

## Status

**Phase 1 — ROS 2 Foundation.** See [`docs/PROGRESS.md`](docs/PROGRESS.md) for live
status and [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full plan.

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
│  ├─ companion_bringup/    ← launch files + config
│  ├─ companion_brain/      ← personality/empathy (stub in Phase 1)
│  └─ companion_face/       ← face renderer (stub in Phase 1)
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
ros2 launch companion_bringup demo.launch.py   # see the brain + face talk
```

> **Note:** ROS 2 runs on **Linux only** — build/run these in WSL2 or on the Pi, not in
> native Windows. The 800-line guard (`python tools/check_file_length.py .`) runs anywhere.

## Rules

All contributors (human or AI) follow [`CLAUDE.md`](CLAUDE.md): small modular files
(≤800 lines), typed message contracts, TDD, clean shutdown, no magic numbers.
