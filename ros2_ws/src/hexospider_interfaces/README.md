# hexospider_interfaces

The **message contracts** — the typed "language" every other node speaks. This is the
integration spine of the robot.

- Build type: **`ament_cmake`** (required for ROS message / `rosidl` generation).
- Defines:
  - `msg/RobotEmotion.msg` — the robot's expressed emotion (Brain → Face/Audio).
  - `msg/HumanEmotion.msg` — the perceived human emotion (Perception → Brain); the
    MOAT rail, defined now, used in Phase 3.

> Rule: nodes never reach into each other's internals — they communicate **only**
> through messages defined here. See the spec at
> `docs/superpowers/specs/2026-05-27-ros2-foundation-design.md`.
>
> _Scaffolded during Phase 1 implementation (package files + `.msg` definitions)._
