# CLAUDE.md — Companion Project Rules

This file is the **authoritative rulebook** for all work in this repository.
Claude (and any human) MUST follow these rules on every change. When a rule here
conflicts with a default habit, **this file wins**.

> One-line summary: Companion is an **emotion-aware AI robot companion**. The Pi 5
> is always the brain (ROS 2 + AI + face + empathy); the body is swappable.
> See `docs/ROADMAP.md` for the vision and `docs/PROGRESS.md` for current status.

---

## 1. Golden rules (non-negotiable)

1. **Small files.** Target **~500 lines** per source file. **Hard cap: 800 lines.**
   An automated check (`tools/check_file_length.py`) fails the build if any file
   exceeds the cap. If a file is growing past ~500 lines, that is a signal it does
   too much — split it.
2. **One responsibility per unit.** Each node, module, class, and function does
   one clear thing. If you can't describe it in one sentence, split it.
3. **Modular & understandable first.** Prefer clear, boring code over clever code.
   A new reader should understand a file without reading the rest of the system.
4. **No dead/feature-creep code (YAGNI).** Build only what the *current phase*
   needs. Future-phase features are documented in the roadmap, not coded early.
   (Exception: message *contracts* may be defined early — they are cheap and
   prevent painful rewrites.)
5. **Tests before claiming done.** Code is not "done" until `colcon test` is green
   and the relevant behavior is demonstrated. Never claim success without evidence.

---

## 2. ROS 2 conventions

- **Distro:** ROS 2 **Jazzy Jalisco** on **Ubuntu 24.04**. (ROS 1 is end-of-life —
  never use it.)
- **Language:** **Python (`rclpy`)** by default. Use C++ only if a proven
  hard-real-time need appears (document the reason first).
- **Packages:** named `companion_*`. Node/logic packages use `ament_python`;
  the interfaces package uses `ament_cmake` (required for message generation).
- **Messages are contracts.** Nodes communicate over **typed messages**, never by
  reaching into each other's internals. Define/extend messages in
  `companion_interfaces`.
- **Topics:** namespaced under `/companion/...` (e.g. `/companion/robot_emotion`).
- **No magic numbers.** All tunables are **declared ROS parameters**, with defaults
  in `companion_bringup/config/*.yaml`.
- **Logging:** use the node logger (`self.get_logger().info(...)`), never `print()`.
- **QoS:** choose deliberately; keep queue depth **bounded** (small, e.g. 10).

---

## 3. Memory-safety conventions

- Always shut down cleanly: wrap spin in `try/finally`, call `destroy_node()` then
  `rclpy.shutdown()` in the `finally`.
- **No unbounded growth:** no ever-growing lists/dicts/buffers. Bound any cache or
  history with a fixed size.
- Release hardware handles (camera, serial, GPIO) in a `finally`/destructor.
- Prefer fixed-rate timers over busy loops.

---

## 4. Testing & quality

- **TDD:** write the failing test first, then the code to pass it.
- **Pure logic** (emotion selection, parsing, math) is tested with `pytest` and
  needs **no running ROS graph or hardware** — so it runs in WSL2.
- **Integration:** a `launch_testing` test spins the real nodes and asserts a
  message flows.
- **Linters must pass:** `ament_flake8`, `ament_pep257` (+ `ruff`/`black` formatting).
- **The full gate:** `colcon build` clean → `colcon test` green (lint +
  800-line guard + unit + integration).

---

## 5. Naming & style

- `snake_case` for files, functions, variables; `PascalCase` for classes;
  `UPPER_SNAKE` for constants.
- Every public module, class, and function has a short docstring saying *what* and
  *why* (not *how*).
- Filenames describe contents: `heartbeat_node.py`, `face_stub_node.py`.

---

## 6. Workflow

- **Develop & unit-test in WSL2 (Ubuntu 24.04).** Deploy to the Pi for hardware tests.
- Build/test/run from `ros2_ws/`:
  ```bash
  cd ros2_ws
  colcon build
  source install/setup.bash
  colcon test && colcon test-result --verbose
  ros2 launch companion_bringup demo.launch.py
  ```
- **Track progress:** after meaningful work, update `docs/PROGRESS.md` (status +
  decision log). This is how we "stay on path."
- **Phase discipline:** check `docs/ROADMAP.md` — only build the current phase.

---

## 7. Where things live

| Path | Purpose |
|------|---------|
| `CLAUDE.md` | These rules (authoritative). |
| `docs/ROADMAP.md` | Vision, MOAT, 4-phase plan, exit criteria. |
| `docs/PROGRESS.md` | Live status + decision log. |
| `docs/superpowers/specs/` | Per-phase design specs. |
| `ros2_ws/src/companion_interfaces/` | Message contracts. |
| `ros2_ws/src/companion_bringup/` | Launch files + config. |
| `ros2_ws/src/companion_brain/` | Personality/empathy (stub in Phase 1). |
| `ros2_ws/src/companion_face/` | Face renderer (stub in Phase 1). |
| `tools/check_file_length.py` | The 800-line guard. |
