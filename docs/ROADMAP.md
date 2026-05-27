# HexoSpider Roadmap

_Last updated: 2026-05-27_

## Vision

An **emotion-aware AI robot companion** with a real personality. It expresses
feelings on an animated 8-bit face (blink, cry, get angry, show art, "handshake"
greetings) and makes sounds. Its **MOAT** (the differentiator): it perceives the
*human's* emotional state and responds with empathy — comforting you when you're
sad, cheering you up, celebrating with you.

## Guiding architecture

- **Pi 5 = the brain** (ROS 2, AI, face, empathy). Always.
- **Body is swappable** (hexapod / robot dog / ESP32-driven). It's just a
  "locomotion node" that plugs into the same backbone.
- **Everything is a ROS 2 node** that talks over **typed message contracts**, so any
  subsystem can be built, tested, and replaced independently.

## Hardware

| Item | Status |
|------|--------|
| Raspberry Pi 5 | ✅ have |
| GPIO LCD screen (for the face) | ✅ have (testing) |
| 13-TOPS Hailo AI HAT+ (vision) | 🛒 planned (Phase 3) |
| Robot body (hexapod **or** robot dog) | 🤔 deciding — see note |
| ESP32 secondary screen | 🤔 maybe |
| Speaker / mic | 🛒 planned (audio) |

> **Body note:** A **Pi-driven body** (e.g. Freenove Robot Dog) fits the plan with
> the least glue. An **ESP32 body** (e.g. Hiwonder MechDog) can't run ROS 2/AI — it
> becomes a body the Pi commands over WiFi/serial via `micro-ROS`. Decision deferred
> to Phase 3; **does not affect Phases 1–2.**

## The subsystems

| # | Subsystem | Role | Phase |
|---|-----------|------|-------|
| A | **Face** | Render the robot's emotion on the LCD | 2 |
| B | **Brain** | Decide robot emotion; empathy logic (the MOAT) | 1 (stub) → 2 → 3 |
| C | **Perception** | Sense human emotion (camera/voice) + sensors (ToF/ultrasonic) | 3 |
| D | **Locomotion** | Move the body (legs/servos) | later |
| E | **Audio** | Sounds + voice | later |
| F | **Secondary display / ESP32** | Offload/extend the face | later |

## Phases

### Phase 1 — ROS 2 Foundation  ← _current_
Build the clean, modular ROS 2 backbone everything plugs into, with quality
guardrails baked in. Two stub nodes prove the pipeline end-to-end (no hardware).
- **Spec:** `docs/superpowers/specs/2026-05-27-ros2-foundation-design.md`
- **Exit criteria:** `colcon build` clean → `colcon test` green (lint + 800-line
  guard + unit + integration) → `ros2 launch hexospider_bringup demo.launch.py`
  shows the Brain emitting emotions and the Face logging them live → committed to git.

### Phase 2 — Emotional Face
Replace the face stub with a real animated 8-bit face on the LCD (blink, cry, angry,
happy, art, greetings). Driven entirely by the `RobotEmotion` topic from Phase 1.
- **Exit criteria:** the LCD shows distinct, smooth animated emotions in response to
  published `RobotEmotion` messages.

### Phase 3 — AI + Sensors + Empathy (the MOAT)
Add the kit's sensors (camera, ToF, ultrasonic) and the AI: perceive the *human's*
emotion (`HumanEmotion`), feed it to a real Brain that reasons with empathy and
drives the face/body. Vision likely uses the 13-TOPS AI HAT+.
- **Exit criteria:** the robot detects a human's emotional state and responds with a
  fitting, caring reaction.

### Phase 4 — Model Fine-Tuning Pipeline
A repeatable pipeline to collect data and fine-tune a model so the companion grows
more capable and personal over time.
- **Exit criteria:** a documented, reproducible pipeline that produces an improved
  model the robot can run.

> Each phase gets its **own spec → plan → build cycle.** We do not skip ahead.
