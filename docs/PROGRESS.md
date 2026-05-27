# Companion Progress Tracker

_Update this after every meaningful chunk of work. This is how we stay on path._

## Current phase: **Phase 1 — ROS 2 Foundation**

### Phase 1 checklist

- [x] Project decomposed into subsystems + 4-phase roadmap agreed
- [x] Key tech decisions locked (ROS 2 Jazzy, Ubuntu 24.04, Python, WSL2+Pi)
- [x] Design approved
- [x] Documentation scaffolded (`CLAUDE.md`, `README.md`, roadmap, this tracker, spec)
- [x] Folder structure created
- [ ] Implementation plan written (`writing-plans`)
- [ ] `companion_interfaces`: `RobotEmotion.msg` + `HumanEmotion.msg` build
- [ ] `tools/check_file_length.py` (800-line guard) + its test
- [ ] `companion_brain`: `heartbeat_node.py` stub (publishes RobotEmotion)
- [ ] `companion_face`: `face_stub_node.py` stub (logs RobotEmotion)
- [ ] `companion_bringup`: `demo.launch.py` + `config/*.yaml`
- [ ] Unit tests (emotion-cycling logic) green
- [ ] `launch_testing` integration test green
- [ ] Linters green (`ament_flake8`, `ament_pep257`)
- [ ] WSL2 setup steps documented + verified
- [ ] Pi setup steps documented
- [ ] **Phase 1 exit criteria met** (see roadmap)

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

## Notes / open questions

- Body locked to the **Freenove Robot Dog Kit**; locomotion node arrives post-Phase-2.
  Upgrades planned: LCD face screen (Phase 2), vision camera + AI hat (Phase 3).
- 13-TOPS Hailo AI HAT+ officially targets Raspberry Pi OS; on Ubuntu its vision
  stack runs in Docker. Revisit in Phase 3.
- Top-level repo folder is still named `HexoSpider` on disk (cosmetic only); can be
  renamed to `Companion` anytime without affecting the build.
