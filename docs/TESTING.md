# Testing Strategy

Companion uses a **three-tier test pyramid**. Lint tests guard style; **behavioral tests
guard the product**. If behavioral tests pass, the robot pipeline works as designed.

Run everything:

```bash
bash scripts/verify_all.sh
```

---

## Tier 0 — Architecture contracts (anti-drift, runs first)

Enforced by `tools/test_companion_architecture.py` against
`docs/ARCHITECTURE_CONTRACTS.md` and `tools/companion_contracts.py`.

| Check | What it prevents |
|-------|------------------|
| Topic namespace + message types | Wrong msg on `/companion/*` topics |
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

Tests run in WSL without hardware. They validate **contracts** the nodes rely on.

| Module | Test file | What must never break |
|--------|-----------|------------------------|
| Command parser | `test_command_grammar.py` | Voice phrases → behavior plans |
| Places memory | `test_places_store.py` | YAML → map coordinates |
| Session buffer | `test_session_memory.py` | Bounded chat history → RAG context |
| Empathy MOAT | `test_human_to_robot.py` | Human affect → robot emotion |
| Detection router | `test_detection_router.py` | person/dog → follow/harass hints |
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
| `test_detector_publishes` | detector_node | `DetectionBatch` on `/companion/detections` |
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
/companion/detections      → detector_node → detection_hint (person/dog)
/companion/human_emotion   → empathy → /companion/robot_emotion
```

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

WSL integration tests cover the **software contract**. On Pi, additionally verify:

- `ros2 launch companion_bringup mentorpi_deluxe.launch.py`
- USB voice + ascamera topics (manual smoke test)
- Nav2 with `simulated_travel_sec: 0`

Hardware tests are documented in [MENTORPI_DELUXE.md](MENTORPI_DELUXE.md).
