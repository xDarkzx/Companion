# companion_face

The **face**: turns the robot's emotion into something you can see. Subscribes to
`RobotEmotion`.

- Build type: **`ament_python`**.
- **Phase 1:** `face_stub_node.py` — subscribes and logs the emotion it would show.
  This proves the pipeline without hardware.
- **Phase 2:** the *insides* of this node become the real **animated 8-bit face** on
  the LCD (blink, cry, angry, happy, art, greetings). Its subscription interface stays
  the same, so nothing upstream changes.

> Keep rendering logic modular and ≤800 lines per file (see `CLAUDE.md`).
>
> _Scaffolded during Phase 1 implementation._
