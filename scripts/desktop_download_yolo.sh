#!/usr/bin/env bash
# Download YOLOv8 nano weights for desktop vision testing.
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_DIR="$ROOT/models"
MODEL_PATH="$MODEL_DIR/yolov8n.pt"

mkdir -p "$MODEL_DIR"

if [[ -f "$MODEL_PATH" ]]; then
  echo "Model already exists: $MODEL_PATH"
  exit 0
fi

if ! python3 -c "import ultralytics" 2>/dev/null; then
  echo "Installing ultralytics..."
  pip3 install --user ultralytics
fi

cd "$MODEL_DIR"
python3 - <<'PY'
from ultralytics import YOLO

YOLO('yolov8n.pt')
print('Downloaded yolov8n.pt')
PY

if [[ ! -f "$MODEL_PATH" ]]; then
  echo "Download failed — expected $MODEL_PATH"
  exit 1
fi

echo ""
echo "Use with:"
echo "  bash scripts/desktop_demo.sh keyboard true $MODEL_PATH"
