# hexospider_bringup

The **"start everything"** package: launch files and configuration. No robot logic
lives here — only how to wire nodes together and what parameters to give them.

- Build type: **`ament_python`**.
- Contains:
  - `launch/demo.launch.py` — starts the Phase 1 Brain + Face stub nodes.
  - `config/demo.yaml` — tunable parameters (publish rate, emotion sequence). **No
    magic numbers in node code — they come from here.**

> _Scaffolded during Phase 1 implementation._
