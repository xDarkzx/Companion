# Spec — Phase 1: HexoSpider ROS 2 Foundation

_Date: 2026-05-27 · Status: approved · Phase: 1 of 4_

## 1. Overview

Build a clean, modular **ROS 2 Jazzy** workspace that serves as the backbone for the
entire HexoSpider robot. Every subsystem will be a **node** communicating over
**typed message contracts**. Phase 1 delivers the skeleton, two stub nodes that prove
the pipeline end-to-end, and automated quality guardrails. **No hardware is required**
— it runs in WSL2 today and identically on the Pi.

## 2. Goals

- A buildable colcon workspace with per-subsystem package layout.
- The **message contracts** that form the integration spine.
- A working **publish → subscribe** demo (stub Brain → stub Face).
- **Automated guardrails**: 800-line file guard, linting, unit + integration tests.
- **Setup docs** for WSL2 and the Pi.

## 3. Non-goals (explicitly out of scope for Phase 1)

No real face graphics, no AI/LLM, no sensors, no servos/locomotion, no audio, no CI,
no Docker. Those belong to later phases (see `docs/ROADMAP.md`).

## 4. Architecture & data flow

```
   Perception (Phase 3)            Brain (Phase 1 stub)           Face (Phase 1 stub)
  ┌────────────────────┐        ┌────────────────────┐        ┌────────────────────┐
  │ senses HUMAN emotion│──────▶│ decides ROBOT emotion│──────▶│ renders face (logs) │
  │  HumanEmotion msg   │  topic │  + empathy (later)   │ topic  │  RobotEmotion msg   │
  └────────────────────┘        └────────────────────┘        └────────────────────┘
        /hexospider/human_emotion          /hexospider/robot_emotion
        (contract defined now, used Phase 3)   (exercised by the Phase 1 demo)
```

Principle: **node-per-responsibility**, typed messages between them, config in YAML,
each node testable in isolation.

## 5. Repository layout

```
HexoSpider/
├─ CLAUDE.md                         # rules
├─ README.md
├─ .gitignore
├─ docs/
│  ├─ ROADMAP.md
│  ├─ PROGRESS.md
│  └─ superpowers/specs/             # this file lives here
├─ tools/
│  └─ check_file_length.py           # 800-line guard
└─ ros2_ws/src/
   ├─ hexospider_interfaces/         # ament_cmake (message generation)
   ├─ hexospider_bringup/            # launch + config (ament_python)
   ├─ hexospider_brain/              # stub heartbeat node (ament_python)
   └─ hexospider_face/               # stub logger node (ament_python)
```

> The `hexospider_interfaces` package must use **`ament_cmake`** because ROS message
> (`rosidl`) generation requires it. The node packages use **`ament_python`**. This is
> the standard ROS 2 mixed-package pattern.

## 6. Message contracts

### `RobotEmotion.msg` — used by the Phase 1 demo
The robot's expressed emotion. Produced by the Brain, consumed by the Face (and later
Audio).

| Field | Type | Meaning |
|-------|------|---------|
| `header` | `std_msgs/Header` | timestamp + frame (standard) |
| `emotion` | `string` | one of the documented constants below |
| `intensity` | `float32` | 0.0 (subtle) → 1.0 (max) |
| `source` | `string` | producer, e.g. `"brain"`, `"manual"` |

Documented emotion constants (defined in the `.msg`):
`NEUTRAL, HAPPY, SAD, ANGRY, CRY, LOVE, SURPRISE, SLEEPY`.

### `HumanEmotion.msg` — defined now, used in Phase 3 (the MOAT)
The perceived emotion of the *human*. Produced by Perception, consumed by the Brain.

| Field | Type | Meaning |
|-------|------|---------|
| `header` | `std_msgs/Header` | timestamp + frame |
| `emotion` | `string` | perceived human affect |
| `confidence` | `float32` | 0.0 → 1.0 |
| `source` | `string` | e.g. `"vision"`, `"voice"` |

Two separate messages (not one) keep producers and consumers clean: Perception →
`HumanEmotion` → Brain → `RobotEmotion` → Face.

## 7. Nodes (Phase 1 stubs)

- **`hexospider_brain/heartbeat_node.py`** — on a timer (rate from config),
  publishes `RobotEmotion` on `/hexospider/robot_emotion`, cycling through a small set
  of emotions. The emotion-selection logic is a **pure function** so it can be unit
  tested without ROS. Declares parameters; logs via the node logger; shuts down cleanly.
- **`hexospider_face/face_stub_node.py`** — subscribes to
  `/hexospider/robot_emotion` and logs `Showing emotion: <name> (<intensity>)`. In
  Phase 2 the *insides* of this file become the real LCD renderer; its topic
  interface does not change.

## 8. Configuration

`hexospider_bringup/config/demo.yaml` holds tunables (e.g. `publish_rate_hz`,
`emotion_sequence`). Nodes use `declare_parameter` with sensible defaults. **No magic
numbers in code.**

## 9. Launch

`hexospider_bringup/launch/demo.launch.py` (Python launch file) starts the Brain and
Face nodes with the config applied.

## 10. Quality guardrails

- **800-line guard** — `tools/check_file_length.py`: pure-Python, configurable limit
  (default 800), skips `build/`, `install/`, `log/`, generated files. Wired into
  `colcon test` (via a pytest test) so an oversized file **fails the build**.
- **Linting/formatting** — `ament_flake8`, `ament_pep257`; `ruff`/`black` formatting.
- **No-leak conventions** — `try/finally` shutdown, bounded QoS depth (e.g. 10), no
  unbounded buffers. Codified in `CLAUDE.md`.

## 11. Testing strategy

- **Unit (pytest, no ROS):** the Brain's emotion-cycling pure function; the
  file-length guard.
- **Integration (`launch_testing`):** spin Brain + Face, assert a `RobotEmotion`
  message is received and logged.
- All runs in WSL2; identical on the Pi.

## 12. Setup (documented in README during implementation)

- **WSL2:** enable WSL2 → install Ubuntu 24.04 → install ROS 2 Jazzy via apt →
  install `colcon` → `colcon build` → run demo.
- **Pi:** flash **Ubuntu Server 24.04** → install ROS 2 Jazzy → clone → build → run.

## 13. Acceptance criteria

1. `colcon build` completes cleanly in WSL2.
2. `colcon test` passes: linters clean, 800-line guard passes, unit + integration
   tests green.
3. `ros2 launch hexospider_bringup demo.launch.py` shows the Brain publishing
   emotions and the Face logging them, live.
4. Repository initialized in git with a sane `.gitignore`.

## 14. Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| ROS 2 install friction on WSL2 | Document exact apt steps; pin to Jazzy |
| Mixed ament_cmake + ament_python confusion | Follow the standard pattern; spec §5 note |
| Scope creep into face/AI | Non-goals (§3) + phase discipline in CLAUDE.md |

## 15. Future hooks (designed-in, not built)

- `HumanEmotion.msg` ready for Phase 3 perception/empathy.
- Per-subsystem packages ready to grow.
- Stub Face's interface is stable so Phase 2 only changes its internals.
