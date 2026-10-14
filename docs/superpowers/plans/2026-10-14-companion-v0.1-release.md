# Companion v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans to implement this
> plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing Companion ROS 2 stack into a public, reviewer-ready repo. It gains
language-driven 3D object finding and is measured on public datasets.

**Architecture:** A ROS-free `companion_vision` library handles detection, depth and 3D
localisation behind small protocols. A thin `grounded_detector_node` exposes the library as a
ROS 2 service and topics, and the agent gains a "where is X" intent. Evaluation scripts run the
same library natively on the GPU and commit their outputs.

**Tech stack:**
- **Robot stack:** ROS 2 Jazzy, rclpy, `vision_msgs`.
- **Models:** Hugging Face `transformers` running OWLv2, Grounding DINO tiny and Depth Anything V2 Metric Indoor Small.
- **Libraries:** numpy, OpenCV, pycocotools, h5py.
- **Tooling:** pytest, ruff, GitHub Actions, Docker.

**Spec:** `docs/superpowers/specs/2026-10-14-companion-v0.1-portfolio-release-design.md`

User preference: plans stay brief. Tasks name their files, interfaces and tests, and code is
written test-first during execution rather than pasted here.

## Global constraints

- **Platform:** ROS 2 Jazzy on Ubuntu 24.04 (Python 3.12) for ROS packages. `companion_vision` supports Python 3.10 or later and imports no `rclpy`.
- **Repo rules (CLAUDE.md):** files under 800 lines (target 500); topics under `/companion/`; parameters declared with defaults in `companion_bringup/config`; queue depth 10 or less; the node logger, never `print`.
- **Licences:** model weights and dependencies must be Apache-2.0, MIT or BSD. No Ultralytics (AGPL). The repo is Apache-2.0.
- **Model revisions:** pinned to these commits.
  - `google/owlv2-base-patch16-ensemble@cfd3195b`
  - `IDEA-Research/grounding-dino-tiny@a2bb814d`
  - `depth-anything/Depth-Anything-V2-Metric-Indoor-Small-hf@8078d68a`. This is a format conversion of the Apache-2.0 checkpoint `Depth-Anything-V2-Metric-Hypersim-Small`; ADR 0003 records the licence.
- **Storage:** `HF_HOME=D:\hf-cache`. Datasets go in `D:\Datasets\companion`. Nothing is written to `C:`, which is 96% full.
- **No silent fallbacks:** if a requested backend fails to load, the node fails loudly. It never quietly switches to a fake or another model.
- **No cost:** no paid APIs.
- **Git:** commits authored by xDarkzx and ending with the Claude co-author line; hooks are never skipped.

## Review focus

1. **Frames arrive faster than inference runs.** Only the latest frame is kept, the service still answers, and memory stays flat. Test in Task 9.
2. **Depth is missing or invalid** (zeros, NaN, too near or too far, reflective surfaces). The result reports no depth and the answer says so; a distance is never guessed. Tests in Tasks 5 and 10.
3. **The query is empty, junk, or matches nothing.** The service returns `found=false` with a clear reason, and the agent says it can't see the object. Tests in Tasks 6 and 10.
4. **Depth and RGB images differ in resolution, or `CameraInfo` hasn't arrived.** Depth is resized to the RGB image with nearest-neighbour sampling. Without intrinsics there is no 3D result and a warning is logged once. Tests in Tasks 5 and 9.
5. **Model weights can't load** (offline, wrong revision, no CUDA). Startup fails with a clear error; it never falls back to a fake. Test in Task 6.

---

## M1: Hygiene and a green gate

### Task 1: Commit the work in progress and remove third-party material

**Files:** `.gitignore` and the whole working tree.

- [ ] Move the root stock art (`*.jpg`, `*.ai`, `*.eps`, the `*_face.png` set, `g327.png`, `blink_*.mp3`) and the folders `reference/`, `extracted_faces/` and `models/` to `D:\DansProject\_companion_private\`. Moving rather than deleting keeps the user's files safe. Delete the stray file `=1.21.6,`.
- [ ] Extend `.gitignore` to cover `build/`, `install/` and `log/` (root and `ros2_ws/`), `.venv/`, `__pycache__/`, `.desktop_deps_ok`, `models/` and `tts/cache/`.
- [ ] Check every file under `assets/` for a recorded licence. Keep only CC0 or self-made files, and record their sources in `assets/SOURCES.md`.
- [ ] Commit the remaining work in progress package by package, with conventional messages (one commit each for agent, behaviours, body, voice, memory, perception, brain, bringup, interfaces, tools and docs).
- [ ] Inspect `Screenshot 2026-05-27 145401.png`, which is in the history. If it isn't project material, strip it from history with `git filter-repo` before the first push.

### Task 2: Make the gate green

**Files:**
- `tools/companion_contracts.py`
- `companion_face/sfx_player.py`
- `companion_voice/*` (lint fixes only)
- `companion_bringup/test/test_remember_fact_flow.py`, or the code it exposes
- `requirements-dev.txt`
- `pyproject.toml`
- every `package.xml`
- `LICENSE`
- the `harass_dog` behaviour, everywhere it appears

- [ ] Register `/companion/tts_playing`, a `std_msgs/Bool` from `tts_node` to `stt_node`, in the contract registry, and add it to `docs/ARCHITECTURE_CONTRACTS.md`.
- [ ] Fix the flake8 and pep257 findings in `companion_face` and `companion_voice`, including the unused `edge_tts` import.
- [ ] Reproduce `test_remember_fact_flow` in the container, find the root cause, and fix the code or the test. A fix that only makes the test pass is not acceptable.
- [ ] Pin `ruff==0.15.x` (the current version) in `requirements-dev.txt`. Make `verify_all.sh` install from that file instead of `pip install ruff`, and fix what the pinned ruff reports under the repo's own `select = E, F, W`.
- [ ] Rename the behaviour `harass_dog` to `play_with_dog` in the code, contracts, config and docs.
- [ ] Set every `package.xml` licence to `Apache-2.0` and add `LICENSE`.
- [ ] Add `docker/ci.Dockerfile`, built from `ros:jazzy-ros-base` with rosdep dependencies and dev requirements, and `scripts/docker_verify.sh`, which builds the image and runs `verify_all.sh` inside it. This is the reviewer's single command.
- [ ] Gate: `bash scripts/docker_verify.sh` ends with `DONE_OK` and 0 failures. Commit.

### Task 3: CI and repository process files

**Files:**
- `.github/workflows/ci.yml`
- `.github/dependabot.yml`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/{bug,feature}.yml`
- `.github/CODEOWNERS`
- `.pre-commit-config.yaml`

- [ ] The `ros` job runs in the `ros:jazzy-ros-base` container with rosdep, `verify_all.sh` and uploaded test results.
- [ ] The `vision` job runs on `ubuntu-24.04` with Python 3.12, installs CPU-only torch and the package, and runs `pytest -m "not models"`. It is added in Task 4, when the package exists.
- [ ] Dependabot covers pip and github-actions, weekly.
- [ ] pre-commit runs ruff, the line guard, end-of-file checks and large-file checks.
- [ ] Commit. Verification happens on the first GitHub push (Task 17).

## M3: `companion_vision`, a ROS-free library

The package is `ros2_ws/src/companion_vision/`. It is an `ament_python` package with no rclpy
imports, and it can also be installed with `pip install -e`. Model libraries are imported lazily
inside the backends, so the package and its fakes import without torch.

### Task 4: Core types and the package skeleton

**Files:** `companion_vision/types.py`, `package.xml`, `setup.py`, `setup.cfg`,
`test/test_types.py`, and lint tests.

**Produces:**
- `Box(x0: float, y0: float, x1: float, y1: float)`, frozen, with `width`, `height`, `area`, `center` and `clip(w, h)`. The constructor raises `ValueError` if `x1 < x0` or `y1 < y0`.
- `Detection2D(label: str, score: float, box: Box)`.
- `Intrinsics(fx: float, fy: float, cx: float, cy: float)`, with `from_fov(width, height, hfov_deg)`.
- `Located(label: str, score: float, box: Box, xyz: tuple[float, float, float] | None)`, with `distance` returning the length of `xyz` or `None`.

- [ ] Write the tests first: Box geometry and validation, clipping, and `from_fov` against a known 90° case (fx = width / 2).
- [ ] Implement, register the package in `verify_all.sh` and `COMPANION_PACKAGES`, add the `vision` CI job, and commit.

### Task 5: Localisation maths

**Files:** `companion_vision/localize.py`, `test/test_localize.py`.

**Produces:**
- `central_region(box: Box, frac: float = 0.5) -> Box`
- `box_depth(depth_m: np.ndarray, box: Box, *, min_m=0.1, max_m=10.0, min_valid=20) -> float | None`: the median over the central region of the box after clipping it to the image. It ignores zero, NaN and out-of-range pixels, and returns `None` if fewer than `min_valid` pixels remain.
- `back_project(u: float, v: float, z: float, k: Intrinsics) -> tuple[float, float, float]`, in the camera optical frame: x right, y down, z forward.
- `align_depth(depth_m: np.ndarray, rgb_shape: tuple[int, int]) -> np.ndarray`, using nearest-neighbour resizing.
- `locate(det: Detection2D, depth_m: np.ndarray | None, k: Intrinsics | None) -> Located`

- [ ] Tests:
  - a synthetic plane at 2.0 m gives `z == 2.0`;
  - background pixels at the box edges don't move the median;
  - an all-zero or all-NaN box gives `None`;
  - a box partly outside the image is clipped;
  - back-projection matches a hand-computed point;
  - `align_depth` handles 320×240 to 640×480;
  - no depth or no intrinsics gives `xyz=None`.
- [ ] Implement and commit.

### Task 6: Detector protocol and backends

**Files:** `companion_vision/detector.py`, `companion_vision/backends/owlv2.py`,
`companion_vision/backends/grounding_dino.py`, `companion_vision/backends/fake.py`,
`test/test_detector.py`, `test/test_backends_models.py` (marker `models`).

**Produces:**
- `class Detector(Protocol): name: str; def detect(self, rgb: np.ndarray, queries: Sequence[str]) -> list[Detection2D]`
- `normalize_queries(queries) -> tuple[str, ...]`: strips, lowercases, collapses whitespace and removes duplicates. Raises `ValueError("empty query")` if nothing is left.
- `load_detector(name: Literal["owlv2", "grounding_dino", "fake"], *, device: str, score_threshold: float, revision: str | None) -> Detector`. It raises `DetectorLoadError` with the cause when weights or libraries are unavailable.
- `FakeDetector(script: dict[str, list[Detection2D]])`: returns scripted detections for each query, for tests.
- The Grounding DINO backend splits queries into prompts that fit its 256-token limit and merges the results.
- Both real backends apply the score threshold and per-label NMS (IoU 0.5) and return at most `top_k=20` detections.

- [ ] Tests:
  - normalisation, including an empty query raising an error;
  - the fake returns its script;
  - `load_detector` maps a missing `transformers` (simulated) to `DetectorLoadError`;
  - the NMS helper drops duplicate boxes.
- [ ] Model tests: each real backend finds a "cat" in a fixed COCO val image (id 39769, two cats) with a score above the threshold.
- [ ] Implement and commit.

### Task 7: Depth sources

**Files:** `companion_vision/depth.py`, `companion_vision/backends/depth_anything.py`,
`test/test_depth.py`.

**Produces:**
- `class DepthSource(Protocol): def depth(self, rgb: np.ndarray, sensor: np.ndarray | None) -> np.ndarray | None`, returning metres.
- `SensorDepth(scale: float = 0.001)` converts uint16 millimetres or float32 metres. A missing frame gives `None`.
- `MonocularDepth(device, revision)` returns metric depth at the RGB resolution.
- `NoDepth()` always returns `None`.
- `load_depth(mode: Literal["sensor", "monocular", "none"], ...)`

- [ ] Tests: uint16 scaling, float passthrough, `None` passthrough, and the mode mapping. A `models` test checks the monocular output has the right shape and lies in 0.1–20 m on a NYU frame.
- [ ] Implement and commit.

### Task 8: Pipeline

**Files:** `companion_vision/pipeline.py`, `test/test_pipeline.py`.

**Produces:**
- `Finder(detector: Detector, depth: DepthSource, intrinsics: Intrinsics | None)`
- `.find(rgb, queries, sensor_depth=None) -> list[Located]`, sorted by score in descending order and aligning depth when needed.
- `.timings`, a dict of the last run's stage times in ms: `detect`, `depth`, `locate`.

- [ ] Tests (fakes only):
  - the sort order;
  - xyz is filled when depth and intrinsics exist and `None` when either is missing;
  - mismatched depth resolution is aligned;
  - timings keys are present.
- [ ] Implement and commit.

## M4: ROS integration

### Task 9: Interfaces and `grounded_detector_node`

**Files:**
- `companion_interfaces/srv/FindObject.srv`
- `companion_interfaces/CMakeLists.txt` and `package.xml` (adding the `vision_msgs` dependency)
- `companion_perception/grounded_detector_node.py`
- `companion_perception/ros_convert.py`
- `companion_perception/test/test_ros_convert.py`
- `companion_bringup/config/perception.yaml`
- `companion_bringup/launch/perception.launch.py`
- `companion_bringup/test/test_find_object_service.py`
- `tools/companion_contracts.py`

**Interfaces:**
- `FindObject.srv`: the request has `string query`. The response has `bool found`, `string reason` (empty, "no match", "no depth", "no camera frame" or "bad query") and `vision_msgs/Detection3DArray objects`.
- The service is `/companion/find_object`. Topics are `/companion/objects` (`vision_msgs/Detection3DArray`) and `/companion/perception/annotated` (`sensor_msgs/Image`).
- `/companion/detections` (`DetectionBatch`) stays, published for the `watch_labels` parameter, because six existing consumers (follow, vision hints and preview) use it. This deviates from spec §4.3, which planned to replace it, and the reason is recorded in ADR 0002.
- Parameters:
  - `backend` (default `owlv2`);
  - `depth_mode` (`sensor`);
  - `score_threshold` (0.2);
  - `watch_labels` (`["person","dog"]`);
  - `watch_rate_hz` (2.0);
  - `rgb_topic`, `depth_topic` and `camera_info_topic`;
  - `device` (`cuda` if available, otherwise `cpu`, resolved once and logged).
- `ros_convert.located_to_detection3d(loc: Located, header) -> vision_msgs.msg.Detection3D` and `locateds_to_array(...)`.

Steps:
- [ ] Replace `detector_node.py` and `yolo_cpu.py` and remove Ultralytics from the scripts and docs. Point `perception.launch.py` at the new node.
- [ ] Unit tests: the conversion keeps label, score and position; the bbox centre equals xyz; a missing xyz gives a zero-size bbox and `reason` "no depth".
- [ ] Integration test with `backend:=fake`:
  - publish a synthetic 640×480 RGB frame, a depth frame at 1.5 m and a `CameraInfo`;
  - call the service with "mug" and assert `found` and z ≈ 1.5;
  - call it with "" and assert `found=false` with reason "bad query";
  - burst 50 frames, then call: it answers within 2 s;
  - call before any frame: reason "no camera frame".
- [ ] Model load failure: launch with `backend:=owlv2` and an invalid revision. The node exits non-zero with `DetectorLoadError` in the log.
- [ ] Update the contracts, `ARCHITECTURE_CONTRACTS.md` and the existing detector tests. The gate goes green. Commit.

### Task 10: The agent's "where is X" intent

**Files:**
- `companion_agent/find_intent.py`
- `companion_agent/object_answer.py`
- `companion_agent/find_object_client.py`
- `companion_agent/agent_node.py`
- tests `test_find_intent.py` and `test_object_answer.py`
- `companion_bringup/test/test_where_is_flow.py`

**Produces:**
- `parse_find(text) -> str | None` accepts "where is the X", "where's my X", "find the X", "can you see a X" and "look for the X", and returns X with articles and "my" removed. Navigation and other commands return `None`.
- `answer_for(query: str, result: Located | None, reason: str) -> str`:
  - **Found:** a distance to one decimal place, and a direction from the bearing angle `atan2(x, z)`: within ±10° is "straight ahead", up to ±35° is "a little to the left/right", beyond that is "to your left/right". For example, "The red mug is about 1.2 metres ahead, a little to the left."
  - **No depth:** "I can see the red mug, but I can't tell how far away it is."
  - **Not found:** "I can't see a red mug right now."
- `FindObjectClient` wraps an async service call with a timeout (3 s default) and gives `reason` "timeout" when it expires.
- The agent publishes the AgentState `retrieving` while searching and `speaking` while answering, using the existing face overlay. No new emotions are added.

Steps:
- [ ] Unit tests cover all three answer types, the bearing boundaries at 10° and 35°, and the phrase grammar, including that "go to the kitchen" is not treated as a find.
- [ ] End-to-end integration test with the fake backend: publish "where is the mug" on `/companion/voice_command` and assert that `/companion/tts_request` contains "mug" and "metres".
- [ ] Keep `agent_node.py` under 500 lines by putting the logic in the new modules. Commit.

## M5: Evaluation

The folder is `eval/`. Each script is a CLI that writes `eval/results/<name>.json` with the
dataset, split, model revisions, device, date and metrics.

### Task 11: COCO detection

**Files:** `eval/coco_detection.py`, `eval/common.py` (data paths, result writer, seed),
`eval/test_common.py`.

- [ ] For each backend, run on all 5,000 val2017 images, using the 80 class names as queries (with "dining table" written as "table" and so on, following the published prompt list recorded in the file). Convert to COCO results JSON and score with `COCOeval`, reporting AP, AP50, AP for small, medium and large objects, and images per second.
- [ ] Commit the result JSON along with any published zero-shot figures for these checkpoints, with citations.

### Task 12: NYU 3D localisation and depth

**Files:** `eval/nyu_localization.py`, `eval/nyu_data.py` (reads the labelled `.mat` with h5py,
the test split from `splits.mat` and the standard Kinect intrinsics), `eval/test_nyu_data.py`.

- [ ] Classes: chair, table, sofa, bed, pillow, lamp, monitor, television, cabinet, door, bottle, cup, book and box. Each is mapped from the NYU `names` table, and the mapping is recorded in the file.
- [ ] Ground truth for each object instance:
  - the bounding box of its mask;
  - its 3D centroid, the median of the back-projected depth over the mask.

  Instances are kept only if they have at least 500 pixels and are not cut by the image edge.
- [ ] Matching: for each image and class, the detector query is the class name, and boxes are matched greedily at IoU 0.5 or above.
- [ ] Report detection recall, plus for matched objects the median 3D error and the share within 10 cm and 25 cm, separately for the sensor-depth path (using the ground-truth depth map) and the monocular path. Monocular depth also gets AbsRel and δ1 over valid pixels with the Eigen crop.
- [ ] Unit tests on a synthetic mask and depth confirm the centroid and box maths. Commit the results.

### Task 13: Latency and the report

**Files:** `eval/latency.py`, `eval/report.py`, `docs/EVALUATION.md`,
`docs/adr/0004-default-backend.md`.

- [ ] Run 200 fixed NYU test frames after 10 warm-up frames, and report p50 and p95 per stage on CUDA and on the CPU. `report.py` renders every result JSON into the tables in `docs/EVALUATION.md`, and CI checks the file is in sync (`report.py --check`).
- [ ] Choose the default backend from accuracy versus latency, write the ADR, and commit.

## M6: Demo media

### Task 14: Webcam demo CLI

**Files:** `companion_vision/demo.py`, `test/test_demo_overlay.py` (overlay drawing on a
synthetic frame).

- [ ] `python -m companion_vision.demo --camera 0 --query "mug" [--hfov 70] [--record out.mp4]` shows a live overlay: the box, the label and score, and distance with direction. It uses monocular depth and intrinsics from `--hfov`, which is documented as an approximation for an uncalibrated webcam.
- [ ] Record clips. Make the README GIFs with ffmpeg (palette method, 640 px wide, under 5 MB each) into `docs/media/`. Collect the failure-gallery stills from the author's own captures. Commit.

### Task 15: Recording the full-stack demo

**Files:**
- `companion_face/face_image_publisher.py` (renders the face off-screen to `/companion/face/image`)
- `companion_bringup/launch/demo_find.launch.py`
- `companion_perception/video_publisher_node.py` (plays an mp4 as a camera, with `CameraInfo` from `--hfov`)
- `tools/record_demo.py` (subscribes to the face image, the annotated image and TTS text, and writes a side-by-side GIF)

- [ ] Run in Docker with the GPU, or on the CPU if GPU passthrough is unavailable: play a recorded clip, send "where is the mug", and record the GIF. A script generates the GIF from the real running stack. Commit.

## M7: Documentation and release

### Task 16: Documentation set

**Files:**
- `README.md`
- `docs/REVIEWING.md`
- `docs/ARCHITECTURE.md`, with a diagram generated by `tools/gen_architecture_diagram.py --check` and run in CI
- `docs/PERCEPTION.md`
- `docs/TESTING.md`
- `docs/HARDWARE.md`
- `docs/ROADMAP.md`
- `docs/adr/0001` to `0005`:
  - 0001: ROS 2 Jazzy and Python;
  - 0002: a ROS-free vision library, and keeping `DetectionBatch` for watch labels;
  - 0003: permissive licences only and removing Ultralytics;
  - 0004: the default backend (from Task 13);
  - 0005: deferring human-emotion recognition;
- `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`
- updates to `CLAUDE.md` and `AGENTS.md`

Steps:
- [ ] Fold the useful content of `DESKTOP_DEV`, `ENTERPRISE_STACK`, `HUMAN_INTERFACE`, `MEMORY_AND_RAG`, `MENTORPI_DELUXE`, `DEPLOY_MENTORPI`, `VISION_AND_HAILO`, `VOICE_HARDWARE` and `SETUP` into the new set, then delete `REPLIES.md` and `PROGRESS.md`. The history moves into `CHANGELOG`.
- [ ] Write the README in the order spec §4.5 sets. Its "What runs where" table lists only what was actually run, with the command for each row.
- [ ] Check every link and every number against `eval/results`. Commit.

### Task 17: Publish

- [ ] Create a public `xDarkzx/Companion` repository with a description, topics and an Apache-2.0 licence. Push `main` up to the end of M1 and M2, and confirm CI goes green.
- [ ] Set branch protection to match Revisa: pull requests required, CI required, linear history. Add labels.
- [ ] Open the M3–M7 work as reviewable pull requests (vision library, ROS integration, evaluation, demo and docs), each with CI green and rebase-merged.
- [ ] Publish the v0.1.0 tag and GitHub release with notes taken from the CHANGELOG.
- [ ] Add a Companion card to the profile README (`xDarkzx/xDarkzx`) and recommend pinning it.

## M8: Optional Pi 5 bring-up (needs the user to connect the Pi)

### Task 18: Pi run

- [ ] Run `pi_install_*` on the Pi 5. Launch the stack and the face on the LCD, and run `eval/latency.py --device cpu` on the Pi. Add a Pi row to "What runs where" and to `docs/EVALUATION.md`.
