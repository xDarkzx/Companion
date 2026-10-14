# Changelog

All notable changes are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-10-15

### Added

- The ROS 2 Jazzy foundation: message contracts, an agent that runs multi-step commands,
  memory of places, people and facts, behaviours, a Nav2 bridge, the face, voice and empathy
  rules, with architecture validators and launch tests.
- `companion_vision`: a ROS-free perception library. It finds objects by name with OWLv2 or
  Grounding DINO, takes depth from an RGB-D camera or a monocular model, and places matches
  in 3D.
- `grounded_detector_node` and the `FindObject` service, with an explicit reason for every
  miss. It also publishes `vision_msgs` detections and an annotated image.
- Agent intent for "where is X", answered by voice with distance and direction.
- Benchmarks on COCO val2017 (detection) and the NYU Depth V2 test split (3D localisation and
  depth). Results are rendered into `docs/EVALUATION.md` and checked in CI.
- A webcam demo (`python -m companion_vision.demo`).
- A face animation rendered from the production renderer.
- Service contracts in the architecture validators, and an architecture diagram generated from
  the contracts and checked in CI.
- One-command Docker gate (`scripts/docker_verify.sh`), GitHub Actions CI, a secret scan,
  Dependabot and pre-commit.
- Apache-2.0 licence, CONTRIBUTING, SECURITY and ADRs 0001–0005.

### Changed

- The startup greeting can be turned off and retimed (`speak_welcome`, `welcome_delay_sec`).
- The `harass_dog` behaviour is renamed `play_with_dog`.
- The documentation is consolidated into architecture, perception, evaluation, testing,
  hardware, setup and roadmap guides.

### Removed

- Ultralytics YOLO (AGPL-3.0), replaced by Apache-2.0 models.
- Voice profiles that cloned real people's voices, and a text-to-speech backend that used an
  unlicensed web service. Only local, open-source speech engines remain.

### Fixed

- `/companion/tts_playing` was used but missing from the topic contracts.
- Lint findings in `companion_face` and `companion_voice`.
- The remember-a-fact integration test read the startup greeting instead of the reply.
- "Where is X" before any camera frame arrived was answered as "I can't see X"; the robot now
  says the camera has not sent a picture yet.
