# Roadmap

## Done (v0.1)

- **ROS 2 Jazzy brain.** Eleven packages talk only through typed, CI-checked contracts:
  agent, memory, behaviours, body (Nav2 bridge), face, voice, empathy rules and perception.
- **Language-driven perception.** Find any named object, place it in 3D from an RGB-D camera
  or a monocular estimate, and answer "where is X" by voice. Benchmarked on COCO and NYU
  Depth V2.
- **Engineering.** One-command Docker gate, CI on every pull request, an architecture diagram
  generated from the contracts, evaluation results kept in sync with the docs, and ADRs.

## Next

1. **Run on the robot.** Bring the stack up on a MentorPi, map a home, and record Pi CPU
   latency alongside the results in [EVALUATION.md](EVALUATION.md).
2. **Calibrate monocular depth per camera.** One reading against a known distance gives a
   scale factor. On NYU a single median scale cuts AbsRel from 0.22 to 0.08 (see
   EVALUATION.md).
3. **Faster perception on the Pi.** Compile the detector for a Hailo-8 accelerator, or use a
   smaller detector for the watch list and keep OWLv2 for explicit questions.
4. **Act on what it finds.** Turn a located object into a Nav2 goal ("go to the mug"), using
   the camera-to-map transform.
5. **Spoken empathy without face analysis.** Respond to what people say about how they feel.
   Facial emotion recognition stays out
   ([ADR 0005](adr/0005-defer-human-emotion-recognition.md)).

## Out of scope

- Training or fine-tuning models.
- Cloud services. Everything runs on the robot or a local machine.
- Motor control. That stays in the body's firmware and Nav2.
