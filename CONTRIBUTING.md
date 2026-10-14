# Contributing

Thanks for looking. These rules apply to every change, from a person or a coding agent.

## Workflow

1. Branch from `main`. `main` is protected: changes land through pull requests with CI green.
2. Write the failing test first, then the code that passes it.
3. Run the gate before opening a pull request:
   ```bash
   bash scripts/docker_verify.sh        # ROS stack: build, lint, unit, launch and architecture tests
   python -m pytest ros2_ws/src/companion_vision/test eval -q    # vision library and eval harness
   ```
4. Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`,
   `test:`, `refactor:`, `build:`, `ci:`, `chore:`, `eval:`.
5. Add a line under "Unreleased" in [CHANGELOG.md](CHANGELOG.md), and an
   [ADR](docs/adr/README.md) if you change a design decision.

## Engineering rules

**Code shape**

- One responsibility per file, node and function. Aim for 500 lines per file; 800 is a hard
  limit enforced in CI.
- Every public module, class and function has a docstring saying what it does and why.
- No speculative code: build what the current milestone needs. Message contracts may be
  defined early.

**ROS 2 (Jazzy, `rclpy`)**

- Nodes talk only through typed messages and services. Register every new topic or service in
  [`tools/companion_contracts.py`](tools/companion_contracts.py), then run
  `python tools/gen_architecture_diagram.py`.
- Topics live under `/companion/`. Parameters are declared, with defaults in
  `companion_bringup/config/*.yaml`; no magic numbers.
- Queue depth is 10 or less. Keep only the latest message when processing is slower than input.
- Log with the node logger, never `print()`. `main()` destroys the node and shuts `rclpy` down
  in `finally`.

**AI components**

- No silent fallbacks: if a requested model cannot load, fail loudly with the cause.
- Explain misses (a reason field, a log line), never return a made-up value.
- Model weights and dependencies must be Apache-2.0, MIT or BSD, pinned to a revision
  ([ADR 0003](docs/adr/0003-permissive-licences-only.md)).
- A change to perception behaviour re-runs the affected benchmark and commits the new result
  file, then `python eval/report.py`.

**Tests**

- Pure logic is tested with pytest and no ROS graph. Cross-node behaviour gets a
  `launch_testing` test in `companion_bringup/test/` that asserts message content.
- The test-honesty validators reject `assert True`, skipped tests and launch tests that don't
  wait for discovery. Don't weaken a test to make it pass.
