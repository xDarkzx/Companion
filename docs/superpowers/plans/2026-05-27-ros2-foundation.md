# Phase 1: ROS 2 Foundation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a clean, modular ROS 2 Jazzy workspace where a stub Brain publishes a typed emotion and a stub Face receives it, with automated quality guardrails — proving the backbone end-to-end with no hardware.

**Architecture:** Node-per-responsibility, communicating over typed messages defined in `companion_interfaces`. Brain logic is split into ROS-free pure functions (unit-testable anywhere) and a thin ROS node wrapper.

**Tech Stack:** ROS 2 Jazzy, Python (`rclpy`), `ament_python` + `ament_cmake`, `colcon`, `pytest`, `launch_testing`, ament linters.

> **Build/test platform note:** ROS 2 builds and runs on **Linux only**. All `colcon`
> commands run in **WSL2 (Ubuntu 24.04)** or on the **Pi**, never on Windows. The
> file-length guard (Task 1) is pure Python and runs anywhere.

---

## File structure (what gets created)

```
tools/check_file_length.py            # 800-line guard (pure Python)
tools/test_check_file_length.py       # its unit tests
ros2_ws/src/companion_interfaces/    # ament_cmake: messages
  package.xml  CMakeLists.txt
  msg/RobotEmotion.msg  msg/HumanEmotion.msg
ros2_ws/src/companion_brain/         # ament_python: stub Brain
  package.xml setup.py setup.cfg resource/companion_brain
  companion_brain/__init__.py
  companion_brain/emotion_cycle.py   # pure logic (ROS-free)
  companion_brain/heartbeat_node.py  # ROS node
  test/test_emotion_cycle.py test/test_flake8.py test/test_pep257.py
ros2_ws/src/companion_face/          # ament_python: stub Face
  package.xml setup.py setup.cfg resource/companion_face
  companion_face/__init__.py
  companion_face/face_stub_node.py
  test/test_flake8.py test/test_pep257.py
ros2_ws/src/companion_bringup/       # ament_python: launch + config
  package.xml setup.py setup.cfg resource/companion_bringup
  companion_bringup/__init__.py
  launch/demo.launch.py  config/demo.yaml
  test/test_demo_launch.py test/test_flake8.py test/test_pep257.py
```

---

## Task 1: File-length guard (runs on Windows too)

**Files:** Create `tools/check_file_length.py`, `tools/test_check_file_length.py`.

- [ ] **Step 1–2:** Write `tools/test_check_file_length.py` with tests for `count_lines`, `find_violations` (over limit, under limit, skips `build/`). Run `python -m pytest tools/test_check_file_length.py -v` → expect FAIL (module missing).
- [ ] **Step 3–4:** Implement `tools/check_file_length.py` (argparse CLI, `iter_source_files` skipping `build/install/log/__pycache__/.git`, `count_lines`, `find_violations`, `main` returning non-zero on violation). Re-run tests → expect PASS.
- [ ] **Step 5:** Commit.

## Task 2: `companion_interfaces` — message contracts

**Files:** `package.xml` (ament_cmake, `rosidl_default_generators`, `member_of_group rosidl_interface_packages`), `CMakeLists.txt` (`rosidl_generate_interfaces` with both msgs, `DEPENDENCIES std_msgs`), `msg/RobotEmotion.msg`, `msg/HumanEmotion.msg`.

- [ ] Define `RobotEmotion.msg`: `std_msgs/Header header`; string constants `NEUTRAL/HAPPY/SAD/ANGRY/CRY/LOVE/SURPRISE/SLEEPY`; `string emotion`; `float32 intensity`; `string source`.
- [ ] Define `HumanEmotion.msg`: `std_msgs/Header header`; constants `UNKNOWN/HAPPY/SAD/UPSET/NEUTRAL`; `string emotion`; `float32 confidence`; `string source`.
- [ ] Verify (WSL2/Pi): `colcon build --packages-select companion_interfaces` then `ros2 interface show companion_interfaces/msg/RobotEmotion`. Commit.

## Task 3: Brain pure logic (TDD)

**Files:** `companion_brain/emotion_cycle.py`, `test/test_emotion_cycle.py`.

- [ ] Write failing tests: cycles in order, wraps around, applies intensity, empty sequence raises `ValueError`, out-of-range intensity raises.
- [ ] Implement `Emotion` dataclass + `select_emotion(tick, sequence, intensity=0.8)`. Run `pytest` → PASS. Commit.

## Task 4: Brain ROS node

**Files:** `package.xml`, `setup.py` (entry point `heartbeat_node = companion_brain.heartbeat_node:main`), `setup.cfg`, `resource/companion_brain`, `__init__.py`, `heartbeat_node.py`.

- [ ] `HeartbeatNode`: declares params `publish_rate_hz`, `emotion_sequence`, `intensity`; publishes `RobotEmotion` on `/companion/robot_emotion` via a timer using `select_emotion`; logs each publish; `main()` uses `try/finally` → `destroy_node()` + guarded `shutdown()`.
- [ ] Verify (WSL2/Pi): `colcon build` + `ros2 run companion_brain heartbeat_node`. Commit.

## Task 5: Face stub node

**Files:** `package.xml`, `setup.py` (`face_stub_node = companion_face.face_stub_node:main`), `setup.cfg`, `resource/companion_face`, `__init__.py`, `face_stub_node.py`.

- [ ] `FaceStubNode`: subscribes `/companion/robot_emotion`, logs `Showing emotion: <e> (<i>) from <src>`; clean shutdown. Commit.

## Task 6: Bringup — config + launch

**Files:** `package.xml`, `setup.py` (installs `launch/` + `config/`), `setup.cfg`, `resource/companion_bringup`, `__init__.py`, `config/demo.yaml`, `launch/demo.launch.py`.

- [ ] `demo.yaml` sets `heartbeat_node` params. `demo.launch.py` starts both nodes, passing the config to the brain.
- [ ] Verify: `ros2 launch companion_bringup demo.launch.py` shows brain publishing + face logging. Commit.

## Task 7: Integration test (launch_testing)

**Files:** `companion_bringup/test/test_demo_launch.py`.

- [ ] `generate_test_description` launches both nodes; a test listener node asserts ≥1 `RobotEmotion` arrives within 10 s and its `emotion` is in the expected set.
- [ ] Verify: `colcon test --packages-select companion_bringup`. Commit.

## Task 8: Lint tests + docs

**Files:** `test/test_flake8.py` + `test/test_pep257.py` in each python package; update `README.md` (WSL2 + Pi setup), `docs/PROGRESS.md`.

- [ ] Add standard ament lint tests to brain/face/bringup.
- [ ] Fill README with exact WSL2 + Pi install/build/run commands.
- [ ] Tick Phase 1 boxes in PROGRESS. Final `colcon build && colcon test` green. Commit.

## Acceptance (Phase 1 done)

`colcon build` clean → `colcon test` green (lint + 800-guard + unit + integration) →
`ros2 launch companion_bringup demo.launch.py` shows live emotions → all committed.
