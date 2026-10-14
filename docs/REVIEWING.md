# Reviewing this repository in ten minutes

This page is for someone deciding how much they trust this code. It names the files worth
reading and the commands that prove the claims.

## 1. Run it (2 minutes, needs only Docker)

```bash
bash scripts/docker_verify.sh
```

This builds a ROS 2 Jazzy container and runs everything CI runs for the robot stack:

- the 800-line guard and ruff;
- the architecture and test-honesty validators;
- `colcon build`;
- every unit and launch test.

It ends with `DONE_OK`.

## 2. Read the core idea (3 minutes)

Asking the robot "where is the mug?" exercises every layer. Follow it through the code:

| Step | File | Look for |
|---|---|---|
| Sentence to intent | [`find_intent.py`](../ros2_ws/src/companion_agent/companion_agent/find_intent.py) | A small grammar, not an LLM: predictable and testable |
| Non-blocking service call | [`find_object_client.py`](../ros2_ws/src/companion_agent/companion_agent/find_object_client.py) | Async call with a timeout; reports exactly once |
| The service contract | [`FindObject.srv`](../ros2_ws/src/companion_interfaces/srv/FindObject.srv) | Every miss carries a reason |
| ROS adapter | [`grounded_detector_node.py`](../ros2_ws/src/companion_perception/companion_perception/grounded_detector_node.py) | Latest frame only (no backlog); exits with code 1 if a model can't load |
| Detection | [`detector.py`](../ros2_ws/src/companion_vision/companion_vision/detector.py) | One threshold, NMS and top-k path for every backend; no silent fallback |
| 3D placement | [`localize.py`](../ros2_ws/src/companion_vision/companion_vision/localize.py) | Robust median over the box centre; returns `None` rather than guessing |
| Spoken answer | [`object_answer.py`](../ros2_ws/src/companion_agent/companion_agent/object_answer.py) | Distance and bearing, and an honest answer for each failure |

## 3. Check the evidence (3 minutes)

| Claim | Evidence |
|---|---|
| It works end to end | [`test_where_is_flow.py`](../ros2_ws/src/companion_bringup/test/test_where_is_flow.py) launches the agent and detector, streams camera frames, asks by voice, and asserts the exact sentence spoken |
| Failures are handled | [`test_find_object_service.py`](../ros2_ws/src/companion_bringup/test/test_find_object_service.py) (no frame, bad query, no match, a 50-frame burst), [`test_where_is_without_camera.py`](../ros2_ws/src/companion_bringup/test/test_where_is_without_camera.py), [`test_detector_load_failure.py`](../ros2_ws/src/companion_bringup/test/test_detector_load_failure.py) |
| The models are measured, not demoed | [EVALUATION.md](EVALUATION.md): COCO detection and NYU Depth V2 3D accuracy, with every number traceable to a result file and a script |
| The docs match the code | The architecture diagram and evaluation tables are generated, and CI fails if they drift: [`gen_architecture_diagram.py`](../tools/gen_architecture_diagram.py), [`report.py`](../eval/report.py) |
| The tests are not gamed | [`validate_test_honesty.py`](../tools/validate_test_honesty.py) rejects `assert True`, skips, and launch tests that don't wait for DDS discovery |

## 4. Judge the decisions (2 minutes)

The [ADRs](adr/README.md) record why things are the way they are:

- why perception is a ROS-free library;
- why only permissively licensed models are used (and why YOLO was removed);
- how the default detector was chosen from the benchmarks;
- why facial emotion recognition was deliberately left out.

## Scope of v0.1

- **Verified environments:** the ROS stack runs in Docker on every pull request, and the models
  run on a desktop GPU and CPU. [HARDWARE.md](HARDWARE.md) lists exactly what runs where. The
  next milestone is the MentorPi body.
- **Monocular depth:** EVALUATION.md measures its scale error on an unseen camera, and the
  roadmap has the per-camera calibration that fixes it.
- **Command grammar:** it covers a fixed command set by design, so behaviour is predictable. A
  local LLM can rephrase replies.
