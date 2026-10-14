#!/usr/bin/env bash
# Run the full quality gate in a clean ROS 2 Jazzy container: one command, no local ROS needed.
#   bash scripts/docker_verify.sh
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="companion-ci:jazzy"

docker build -f "$ROOT/docker/ci.Dockerfile" -t "$IMAGE" "$ROOT"

# The repo is mounted read-only and copied, so build output never lands in the working tree.
MSYS_NO_PATHCONV=1 docker run --rm -v "$ROOT:/src:ro" "$IMAGE" bash -c '
  set -eo pipefail
  tar -C /src --exclude=./ros2_ws/build --exclude=./ros2_ws/install --exclude=./ros2_ws/log \
      --exclude=./.venv --exclude=./.git -cf - . | tar -C /ws -xf -
  bash scripts/verify_all.sh
'
