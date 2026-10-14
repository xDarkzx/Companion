# Architecture Contracts (Ground Truth)

This document is the **authoritative architecture reference** for Companion.
CI enforces it via `tools/companion_contracts.py` and
`tools/test_companion_architecture.py`. If code or docs disagree with this
file, **fix the code** — do not weaken the tests.

Sources: `CLAUDE.md`, `docs/ENTERPRISE_STACK.md`, `docs/HUMAN_INTERFACE.md`,
`companion_interfaces/*.msg`.

---

## ROS 2 baseline

| Rule | Value |
|------|-------|
| Distro | **Jazzy Jalisco** on Ubuntu 24.04 |
| Language | **Python (`rclpy`)** unless documented exception |
| Package prefix | `companion_*` |
| Custom topics | **`/companion/...`** namespace |
| QoS queue depth | **≤ 10** (bounded) |
| Logging | `get_logger()` — **no `print()`** in nodes |
| Shutdown | `try/finally` → `destroy_node()` → `rclpy.shutdown()` |
| File size | **target ≤ 500 lines**, **hard cap 800** |

---

## Modularity

| Package | Responsibility |
|---------|----------------|
| `companion_interfaces` | Message contracts only |
| `companion_agent` | Voice/text → multi-step plans |
| `companion_memory` | Places + people YAML |
| `companion_behaviors` | Behavior → face emotion + status |
| `companion_body` | Nav bridge + body status |
| `companion_perception` | Camera, detections, human emotion stub |
| `companion_brain` | Empathy MOAT + demo heartbeat |
| `companion_face` | LCD / ASCII face renderer |
| `companion_voice` | STT / TTS |
| `companion_bringup` | Launch + config only |

Nodes communicate over **typed messages**, never by reaching into other packages.

---

## Topic graph

| Topic | Message | Publishers | Subscribers |
|-------|---------|------------|-------------|
| `/companion/robot_emotion` | `RobotEmotion` | brain, behaviors | face, voice (expressive TTS) |
| `/companion/human_emotion` | `HumanEmotion` | perception | brain (empathy) |
| `/companion/behavior_request` | `BehaviorRequest` | agent | behaviors, body |
| `/companion/voice_command` | `String` | voice | agent |
| `/companion/agent_state` | `AgentState` | agent, voice | face |
| `/companion/tts_request` | `String` | agent | voice |
| `/companion/tts_playing` | `Bool` | voice (tts) | voice (stt mutes while speaking) |
| `/companion/nav_status` | `String` | body | agent |
| `/companion/detections` | `DetectionBatch` | perception | body (follow), face (preview) |
| `/companion/detection_hint` | `String` | perception | agent |
| `/companion/body_status` | `String` | body | — |
| `/companion/behavior_status` | `String` | behaviors | — |
| `/companion/camera_status` | `String` | perception | — |
| `/goal_pose` | `PoseStamped` | body | Nav2 |

External vendor topics (not under `/companion/`): MentorPi ascamera RGB/depth
(see `companion_perception/mentorpi_camera.py`).

---

## Behavior vocabulary

`BehaviorRequest.behavior` must be one of:

`idle`, `follow`, `patrol`, `go_to_place`, `play_with_dog`, `explore`, `stop`, `go_home`

Each maps to a face emotion via `companion_behaviors/behavior_modes.py`
(`BEHAVIOR_EMOTIONS`).

---

## Navigation lifecycle

`/companion/nav_status` strings (from `companion_body/nav_status.py`):

`idle` → `navigating` → `arrived` | `failed` | `following` (follow mode)

Agent **must wait** for `arrived` before multi-step step 2 when `wait_for_nav: true`.
`stop` behavior **must cancel** in-flight navigation.

---

## Shipped places (map frame)

From `companion_bringup/config/places.yaml` (documented in `HUMAN_INTERFACE.md`):

| Place | x | y | yaw |
|-------|---|---|-----|
| kitchen | 3.2 | 1.1 | 1.57 |
| bedroom | -1.0 | 4.5 | 0.0 |
| dock | 0.0 | 0.0 | 0.0 |

Integration tests assert these coordinates on `/goal_pose`.

---

## Empathy MOAT

`companion_brain/human_to_robot.py` mapping (confidence gate **0.35**):

| Human | Robot | Intensity |
|-------|-------|-----------|
| happy | happy | 0.85 |
| sad | love | 0.90 |
| upset | sad | 0.75 |
| neutral | neutral | 0.60 |
| unknown | neutral | 0.50 |

---

## Launch ↔ executable registry

Every `executable=` in `companion_bringup/launch/*.launch.py` must exist in
that package's `setup.py` `console_scripts`. CI validates this mapping.

---

## Test tiers

See `docs/TESTING.md`. **Tier 0** (architecture contracts) runs before colcon
and catches structural drift that behavioral tests cannot see.
