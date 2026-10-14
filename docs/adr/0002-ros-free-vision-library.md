# 0002. A ROS-free vision library behind a thin node

- Status: Accepted
- Date: 2026-10-14

## Context

Language-driven object finding needs PyTorch models, GPU access, benchmarks on public datasets
and a webcam demo. None of that needs ROS, and ROS makes it slower to test: every test would
need a running graph, and the benchmarks would have to run inside a ROS container.

The existing `DetectionBatch` topic on `/companion/detections` already feeds six consumers
(following a person, vision hints to the agent, the preview window).

## Decision

- `companion_vision` is a plain Python package with no `rclpy` import: small protocols
  (`Detector`, `DepthSource`), pure localisation maths and a `Finder` pipeline. It installs with
  pip on any OS. Model libraries are imported only when a real backend loads.
- `grounded_detector_node` in `companion_perception` adapts it to ROS: it converts messages,
  keeps only the latest frame, serves `FindObject` and publishes results.
- The node keeps publishing `DetectionBatch` for a configurable watch list, so the existing
  consumers did not change. New consumers should use `/companion/objects` or the service.

## Consequences

The library's tests run in a plain Python CI job in seconds, the benchmarks run natively on the
GPU, and the same code serves the robot, the demo and the evaluation. The cost is a small
conversion layer (`ros_convert.py`) and two output formats on the perception side.
