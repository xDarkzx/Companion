# companion_brain

The **decision-maker**: chooses what the robot should feel and (later) reasons with
empathy about the human. Publishes `RobotEmotion`.

- Build type: **`ament_python`**.
- **Phase 1:** `heartbeat_node.py` — a stub that publishes `RobotEmotion` on a timer,
  cycling through emotions. The emotion-selection is a **pure function** (unit-tested
  without ROS).
- **Phase 2/3:** grows into the real personality + the **empathy logic** (the MOAT) —
  consuming `HumanEmotion` and deciding a caring response.

> Keep files focused and ≤800 lines (see `CLAUDE.md`). Split as it grows.
>
> _Scaffolded during Phase 1 implementation._
