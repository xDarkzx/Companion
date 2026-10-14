# 0001. ROS 2 Jazzy, Python nodes, typed contracts checked in CI

- Status: Accepted
- Date: 2026-05-27, revised record 2026-10-14

## Context

Companion's brain runs on a Raspberry Pi 5 and has to drive whatever body it is mounted on, so
it needs a robotics middleware with drivers, navigation and tooling. ROS 1 reached end of life
in May 2025. Jazzy is the ROS 2 long-term release that targets Ubuntu 24.04, the OS the Pi runs.

A ROS system can rot quietly: a node starts publishing on a topic nobody documented, a message
type changes, a launch file points at an executable that no longer exists. Nothing fails until
the robot misbehaves.

## Decision

- ROS 2 Jazzy on Ubuntu 24.04. Nodes in Python (`rclpy`); C++ only for a measured real-time need.
- Every topic and service is registered in `tools/companion_contracts.py` with its type and the
  packages allowed to publish, subscribe, serve or call. Static validators in `tools/` fail CI on
  any undocumented, mistyped or unwired topic or service, on unbounded queues, on `print()` in
  nodes, and on files over 800 lines.
- The architecture diagram in `docs/ARCHITECTURE.md` is generated from the same registry, and CI
  fails if it is stale.

## Consequences

The topic graph a reviewer reads is the one the code runs. Adding a topic costs one registry
entry. Python limits control-loop rates, which is acceptable because motor control stays in the
body's own firmware and Nav2.
