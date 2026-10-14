#!/usr/bin/env bash
# Optional CPU vision deps for Phase 3 (YOLO on Pi before Hailo).
set -eo pipefail

echo ">>> Python vision deps (optional Ultralytics YOLO)"
pip3 install --user 'numpy<2' ultralytics 2>/dev/null || {
  echo "WARN: ultralytics not installed — detector stays in stub mode"
}

echo "DONE_OK — set model_path in config/perception.yaml (e.g. yolov8n.pt)"
