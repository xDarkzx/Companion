# Testing strategy

Lint tests guard style; **behavioural tests guard the product**. The ROS tiers below run in CI
in a clean ROS 2 Jazzy container on every pull request, and locally with one command:

```bash
bash scripts/docker_verify.sh     # or, on a machine with ROS 2 Jazzy: bash scripts/verify_all.sh
```

The vision library and the evaluation harness have their own tier (Tier 4), which needs no ROS.

---

## Tier 0 — Architecture contracts (anti-drift, runs first)

Enforced by the tests in `tools/` against the registry in `tools/companion_contracts.py`.

| Check | What it prevents |
|-------|------------------|
| Topic namespace + message types | Wrong msg on `/companion/*` topics |
| Service contracts (`test_service_contracts.py`) | Unregistered, mistyped or orphaned services |
| Generated architecture diagram | `docs/ARCHITECTURE.md` drifting from the registry |
| Licence metadata (`test_package_metadata.py`) | A package declaring a different licence |
| Publisher/subscriber package map | Nodes bypassing layer boundaries |
| Launch executable registry | Launch files referencing nonexistent nodes |
| 500-line soft / 800-line hard cap | Monolithic files |
| No `print()` in nodes | ROS logging guideline violations |
| `destroy_node` + `rclpy.shutdown` | Memory leaks / dirty shutdown |
| QoS depth ≤ 10 | Unbounded queues |
| Behavior vocabulary sync | `.msg` vs `behavior_modes.py` drift |
| Places YAML vs docs | Wrong kitchen coordinates in tests |
| Empathy MOAT sync | `human_to_robot.py` vs empathy_node param drift |

If Tier 0 fails, the architecture is wrong — fix before adding features.

### Anti-fudge rules (test_suite_honesty.py)

These run in CI and **fail the build** if tests are weakened:

| Rule | Prevents |
|------|----------|
| No `assert True` / `@pytest.mark.skip` | Empty or disabled tests |
| Launch tests with publishers must `wait_for_subscribers` | Passing due to DDS race luck |
| Listener launch tests must `warm_up_dds` | Missing messages counted as pass |
| No `assertAlmostEqual(..., places=1)` on map coords | Loose coords that hide wrong nav |
| Required integration test manifest | Deleting critical tests silently |
| Negative validator proofs | Architecture scanner that always passes |
| Topic graph wired in code | Documented topics with no real pub/sub |
| `places_contract.py` single source | Kitchen coords drift vs docs |

---

## Tier 1 — Lint & build (necessary, not sufficient)

| Check | What it proves |
|-------|----------------|
| `ament_flake8` / `ament_pep257` | Code style per package |
| `ruff` | Syntax and obvious bugs |
| `check_file_length.py` | Files stay modular (≤800 lines) |
| `colcon build` | Messages and packages compile |

These do **not** prove the robot understands commands or navigates correctly.

---

## Tier 2 — Unit / contract tests (pure logic, no ROS graph)

These need no ROS graph and no hardware. They validate the **contracts** the nodes rely on.

| Module | Test file | What must never break |
|--------|-----------|------------------------|
| Command parser | `test_command_grammar.py` | Voice phrases → behavior plans |
| Places memory | `test_places_store.py` | YAML → map coordinates |
| Session buffer | `test_session_memory.py` | Bounded chat history → RAG context |
| Empathy MOAT | `test_human_to_robot.py` | Human affect → robot emotion |
| Detection router | `test_detection_router.py` | person/dog → follow/play hints |
| Vision react | `test_vision_react.py` | Hint gating + cooldown rules |
| Goal poses | `test_goal_pose_builder.py` | Place → Nav2 PoseStamped |
| Patrol animation | `test_patrol_animator.py` | Emotion cycle during patrol |
| Camera health | `test_camera_status.py` | stale vs ready logic |

---

## Tier 3 — Integration tests (launch_testing, real nodes)

These spin **actual ROS 2 nodes** and assert **message flows** on production topics.

| Test | Nodes launched | Proves |
|------|----------------|--------|
| `test_companion_pipeline` | agent + behaviors + nav_bridge | Voice → nav goal coords → behaviors → face |
| `test_stack_command` | agent + nav_bridge | Multi-step: kitchen then patrol |
| `test_stop_aborts_plan` | agent + nav_bridge | STOP cancels pending patrol |
| `test_nav_stop_cancels` | agent + nav_bridge | STOP cancels in-flight nav → idle |
| `test_unknown_place_rejected` | agent + nav_bridge | Unknown place → no `/goal_pose` |
| `test_nav_arrival_gate` | agent + nav_bridge | Patrol waits for nav arrival |
| `test_vision_hint_triggers` | agent | Detection hint → follow (`source=vision`) |
| `test_vision_hint_blocked_during_nav` | agent + nav_bridge | Hints ignored during active plan |
| `test_follow_publishes_goal` | nav_bridge | Follow + person → `/goal_pose` at anchor |
| `test_patrol_cycles_waypoints` | nav_bridge | Patrol → kitchen then bedroom goals |
| `test_find_object_service` | grounded_detector_node (fake backend) | FindObject: no frame, found at 1.5 m in 3D, bad query, no match, answer after a 50-frame burst |
| `test_where_is_flow` | agent + grounded_detector_node | "where is the mug" → spoken distance and direction; unknown object → "can't see" |
| `test_where_is_without_camera` | agent | No perception running → "I can't check my camera right now" within the timeout |
| `test_detector_load_failure` | grounded_detector_node | A backend that cannot load logs `DetectorLoadError` and exits with code 1 |
| `test_detector_camera_frame` | grounded_detector_node | Watch batches go from `waiting_for_camera` to the detected label |
| `test_remember_fact_flow` | agent | A remembered fact is retrieved and spoken back |
| `test_behavior_emotion_contract` | behavior_controller | Every behavior → correct `RobotEmotion` |
| `test_agent_tts` | agent | Commands → `/companion/tts_request` |
| `test_empathy_flow` | empathy_node | `HumanEmotion` sad → `RobotEmotion` love |
| `test_demo_launch` | heartbeat + face_stub | Phase 1 emotion topic alive |

### Critical topic contracts under test

```
/companion/voice_command   → agent → /companion/behavior_request
                                      → /goal_pose (kitchen x=3.2 y=1.1)
                                      → /companion/robot_emotion
                                      → /companion/agent_state
/companion/detection_hint  → agent (when react_to_vision) → behavior_request
/companion/detections      → grounded_detector_node (watch list) → detection_hint (person/dog)
/companion/find_object     → grounded_detector_node → found, reason, 2D + 3D detections
/companion/human_emotion   → empathy → /companion/robot_emotion
```

---

## Tier 4 — Vision library and evaluation (no ROS)

| Suite | Runs where | What it proves |
|---|---|---|
| `companion_vision/test` (fakes) | CI `vision` job, Python 3.12, CPU | Box maths, localisation (missing or invalid depth gives no position), detector contract, pipeline ordering and depth alignment |
| `companion_vision/test/test_backends_models.py` | `COMPANION_MODEL_TESTS=1` on a GPU machine | Real OWLv2 and Grounding DINO find both cats in COCO image 39769 at IoU > 0.7 against the ground truth; monocular depth is metric and the right size |
| `eval/test_*.py` | CI `vision` job | COCO conversion, NYU ground-truth extraction, matching, depth metrics, report rendering |
| `eval/report.py --check` | CI `vision` job | `docs/EVALUATION.md` matches the committed result files |

The benchmarks themselves are described in [EVALUATION.md](EVALUATION.md).

---

## What we deliberately removed

Tests that only checked constants exist (topic strings, `isinstance(bool)`,
`startswith('/')`) were **deleted**. They gave false confidence and did not
exercise system behavior.

---

## Adding new tests

1. **Pure logic?** → Tier 2 in the owning package, no `rclpy.spin`.
2. **Cross-node flow?** → Tier 3 in `companion_bringup/test/`, use `ros_test_helpers.py`.
3. Assert **message content and ordering**, not file existence.
4. Run `bash scripts/verify_all.sh` before claiming done.

---

## Pi / hardware

The integration tests cover the **software contract**. On a Pi, also verify:

- `ros2 launch companion_bringup mentorpi_deluxe.launch.py`
- USB voice + ascamera topics (manual smoke test)
- Nav2 with `simulated_travel_sec: 0`

Hardware status and deployment are documented in [HARDWARE.md](HARDWARE.md).
