# Companion Progress Tracker

_Update this after every meaningful chunk of work. This is how we stay on path._

## Current phase: **Phase 1 — ROS 2 Foundation**

### Phase 1 checklist

- [x] Project decomposed into subsystems + 4-phase roadmap agreed
- [x] Key tech decisions locked (ROS 2 Jazzy, Ubuntu 24.04, Python, WSL2+Pi)
- [x] Design approved
- [x] Documentation scaffolded (`CLAUDE.md`, `README.md`, roadmap, this tracker, spec)
- [x] Folder structure created
- [x] Implementation plan written (`docs/superpowers/plans/2026-05-27-ros2-foundation.md`)
- [x] `tools/check_file_length.py` (800-line guard) + tests — **✅ verified on Windows (7/7); repo passes**
- [x] `companion_brain` emotion-cycling pure logic + tests — **✅ verified on Windows (5/5)**
- [x] `companion_interfaces`: `RobotEmotion.msg` + `HumanEmotion.msg` (+ package.xml/CMake) — *written*
- [x] `companion_brain`: `heartbeat_node.py` stub (publishes RobotEmotion) — *written*
- [x] `companion_face`: `face_stub_node.py` stub (logs RobotEmotion) — *written*
- [x] `companion_bringup`: `demo.launch.py` + `config/demo.yaml` — *written*
- [x] `launch_testing` integration test authored — *written*
- [x] ament `flake8` + `pep257` lint tests authored — *written*
- [x] WSL2 + Pi setup steps documented (`docs/SETUP.md`)

### ✅ Verified on Linux (WSL2, ROS 2 Jazzy) — 2026-05-27

- [x] ROS 2 Jazzy installed in WSL2 (Ubuntu 24.04) via `scripts/wsl_install_ros2.sh`
- [x] `colcon build` clean — all 4 packages
- [x] `colcon test` green — **12 tests, 0 errors, 0 failures** (flake8 + pep257 + unit + launch integration)
- [x] `ros2 launch companion_bringup demo.launch.py` shows live brain → face emotion flow
- [x] **🎉 Phase 1 exit criteria MET — foundation complete**

## Decision log

| Date | Decision | Why |
|------|----------|-----|
| 2026-05-27 | Build order: ROS scaffolding → face → AI+sensors → fine-tuning | Solid frame before features |
| 2026-05-27 | ROS 2 **Jazzy**, not ROS 1 | ROS 1 is end-of-life (May 2025) |
| 2026-05-27 | **Ubuntu Server 24.04** on the Pi | Tier-1 ROS 2 support; lean for a robot |
| 2026-05-27 | **Python (`rclpy`)** default language | Fast iteration; matches kit libs; first-class in ROS 2 |
| 2026-05-27 | Dev in **WSL2**, deploy to **Pi** | Fast local test loop without reflashing |
| 2026-05-27 | Phase 1 scope = **B (Foundation-complete)** | MOAT is a real product; guardrails matter |
| 2026-05-27 | Two messages: `RobotEmotion` + `HumanEmotion` | Clean producers/consumers; MOAT rail ready |
| 2026-05-27 | **Body = Freenove Robot Dog Kit** (Pi-driven) | Least-glue body; Pi stays the brain; no architecture change |
| 2026-05-27 | Renamed project `HexoSpider` → **`Companion`** (`companion_*`) | Body-agnostic name; never feels wrong as the body changes |

## Parked for later phases (recorded so we don't lose them — NOT built now)

- **Locomotion (later phase):** wrap **Freenove's built-in IK/gait library** as a ROS 2
  node subscribing to a velocity/command topic. **Do NOT use Isaac Sim / RL** — the
  Freenove dog is hobby position-servo hardware (no torque control / joint feedback), so
  learned policies won't transfer (huge sim-to-real gap) and need an RTX GPU. Isaac/RL is
  only worth it for torque-controlled research robots, not this body.
- **Perception AI (Phase 3):** YOLO (person/object detection) + a face-emotion model for
  the MOAT. Run inference on the **Hailo 13-TOPS hat** (its model zoo + compiler) or
  ONNX/TFLite. These are downloaded/converted models — no training rig to begin. Good job
  for parallel agents *when we reach Phase 3*.
- **Fine-tuning (Phase 4):** the place for any custom model training/data pipeline.

## Notes / open questions

- Body locked to the **Freenove Robot Dog Kit**; locomotion node arrives post-Phase-2.
  Upgrades planned: LCD face screen (Phase 2), vision camera + AI hat (Phase 3).
- 13-TOPS Hailo AI HAT+ officially targets Raspberry Pi OS; on Ubuntu its vision
  stack runs in Docker. Revisit in Phase 3.
- Top-level repo folder is still named `HexoSpider` on disk (cosmetic only); can be
  renamed to `Companion` anytime without affecting the build.
