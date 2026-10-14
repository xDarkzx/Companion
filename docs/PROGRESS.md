# Companion Progress Tracker

_Update this after every meaningful chunk of work. This is how we stay on path._

## Current phase: **Phase 2 — Emotional Face + enterprise building blocks**

### Voice layer (2026-05-28)

- [x] **`companion_voice`** — `stt_node` + `tts_node` stubs
- [x] **`config/voice.yaml`** — ALSA devices, Whisper model, STT mode
- [x] **`voice.launch.py`** + `enable_voice` on companion_stack
- [x] **`scripts/pi_install_voice.sh`** — ALSA + faster-whisper on Pi
- [x] **`docs/VOICE_HARDWARE.md`** — WonderEcho Pro, ReSpeaker, setup
- [x] Whisper capture loop scaffold (`whisper_capture.py` + background thread)
- [x] Agent speaks acknowledgments via `/companion/tts_request`
- [x] Piper / espeak TTS (`piper_player.py` + `tts_node` modes)
- [x] **`mentorpi_deluxe.launch.py`** — full Pi stack (body + voice + camera + agent)
- [x] **`camera_watch_node`** — HD depth camera health on `/companion/camera_status`
- [x] **Nav2 action client** — real `navigate_to_pose` on Pi (sim fallback in WSL)
- [x] **`scripts/verify_all.sh`** — Tier 0 (24) + honesty (8) + colcon (**124 ROS tests**)
- [x] **`docs/DESKTOP_DEV.md`** — PC/WSL: mic + face + memory before Pi deploy
- [x] **`scripts/desktop_demo.sh`** — one-command PC prototype launcher
- [x] **`scripts/desktop_install_deps.sh`** + **`desktop_download_yolo.sh`**
- [x] Desktop TTS auto mode (espeak when installed) + startup welcome message
- [x] Live RGB camera → `detector_node` (`image_bridge.py`, `use_camera` param)
- [ ] YOLO + Hailo on depth/RGB streams (set `model_path` on Pi; Hailo Phase 3+)

### Human interface layer (2026-05-28)

- [x] **`AgentState.msg`** — RAG/LLM lifecycle (listening → retrieving → thinking → acting)
- [x] **Cloud badge on face** — pulsing indicator when cloud/brain active (Emo-style)
- [x] **`rag_retriever.py`** — structured memory lookup (places + people YAML + facts)
- [x] **`docs/MEMORY_AND_RAG.md`** — memory tiers, RAG design, ChatGPT integration plan
- [ ] Vector RAG store (chromadb / embeddings) — Phase 3+
- [ ] OpenAI / Ollama LLM loop with tool calls — Phase 3b
- [x] Session chat buffer — `SessionBuffer` in agent
- [x] `remember_fact` write-back — `FactStore` + "remember that …" voice command

### Human interface — commands & places (2026-05-28)

- [x] **`companion_memory`** — `places.yaml` + `people.yaml` loaders
- [x] **Compound commands** — `go to kitchen and patrol` multi-step plans
- [x] **`go_to_place`** behavior + `nav_bridge_node` → `/goal_pose`
- [x] **Patrol face animations** — emotion cycle during patrol
- [x] **`docs/HUMAN_INTERFACE.md`** — commands, memory, priority, examples
- [x] **`docs/VISION_AND_HAILO.md`** — AI vs motors, Hailo hat role
- [x] **Nav arrival gating** — `/companion/nav_status` + agent waits before step 2
- [x] **`docs/TESTING.md`** — four-tier pyramid (architecture + lint + unit + integration)
- [x] **`docs/ARCHITECTURE_CONTRACTS.md`** — ground-truth topic graph + CI enforcement
- [x] Tier 0 architecture validators (topics, launch registry, 500/800 lines, MOAT sync)
- [x] Test honesty gate — anti-fudge rules, negative validator proofs, required integration manifest
- [x] Integration: pipeline, stop-abort, nav cancel, unknown place, behavior→emotion contract
- [x] Vision hints → agent (`react_to_vision`, `/companion/detection_hint`)
- [x] Parametrized command grammar + empathy MOAT + session buffer contracts
- [ ] Real Nav2 action feedback on Pi (`simulated_travel_sec: 0`)
- [x] Whisper USB mic capture loop (`mode: whisper` on Pi)
- [ ] NASA ROSA for free-form speech (Phase 3b)

### Enterprise stack scaffold (2026-05-28)

- [x] `BehaviorRequest.msg` — voice/agent → behavior contract
- [x] `companion_agent` — intent router + `agent_node` (`/companion/voice_command`)
- [x] `companion_behaviors` — `behavior_controller_node` → `RobotEmotion`
- [x] `companion_body` — vendor probe + `body_status_node`
- [x] `companion_perception` — `detector_node` + camera RGB subscription
- [x] `companion_stack.launch.py` + `mentorpi_body.launch.py`
- [x] `scripts/fetch_mentorpi_vendor.sh` + `scripts/pi_install_nav2.sh`
- [x] `docs/ENTERPRISE_STACK.md` + `docs/DEPLOY_MENTORPI.md`
- [x] Run `fetch_mentorpi_vendor.sh` + `colcon build` with vendor on WSL/Pi
- [x] Wire Nav2 follow/patrol in `companion_body` (`motion_controller`, detection-driven follow)
- [x] Follow/patrol motion status on `/companion/body_status` + `following` nav status
- [ ] NASA ROSA + Whisper on Pi (Phase 3)

### Phase 2 in progress (2026-05-28)

- [x] **Scrapped PNG/image face path** — back to procedural ASCII blue-square eyes (`ascii_renderer.py`)
- [x] `face_ascii_node` — 480×320 blink + all 8 `RobotEmotion` moods + cute SFX (blink/yawn/beeps)
- [x] `personality.py` + `voice_demo_node` — needy/playful reactions to stub voice events
- [x] `demo_face.launch.py` — voice demo → ASCII face pipeline
- [ ] Real STT / voice commands → `VoiceEvent`
- [ ] Emo-style TTS (see [EmojiVoice](https://github.com/rosielab/emojivoice), [OLAF](https://github.com/kamalkantsingh10/OLAF) R2 beeps)
- [ ] Wire face to GPIO LCD on Pi

## Phase 1 — ROS 2 Foundation ✅ complete

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

### ✅ Verified on Linux (WSL2, ROS 2 Jazzy) — 2026-05-28

- [x] `bash scripts/verify_all.sh` green — **109 tests**, 0 failures (flake8 + pep257 + unit + integration)
- [x] Integration: stack command, agent TTS, nav arrival gate, demo launch

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
| 2026-05-28 | **MentorPi Deluxe target** — Ackermann + depth cam + voice box | Primary body for Pi 5 deployment |
| 2026-05-28 | **ASCII face, not PNG** | Image pipeline degraded art; procedural grid matches LCD + Phase 2 |
| 2026-05-28 | **Enterprise building blocks** — agent, behaviors, body, perception | Professional Nav2 + vendor + Companion layers |
| 2026-05-28 | **Vision hints → agent** — `react_to_vision` + cooldown | Phase 3 MOAT: person/dog detections can trigger follow/play when idle |

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
