#!/usr/bin/env bash
# Voice stack for Companion on Pi: ALSA tools + optional faster-whisper.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo ">>> ALSA utilities"
sudo apt-get update -y
sudo apt-get install -y alsa-utils portaudio19-dev python3-pip

echo ">>> Python voice deps (user pip)"
pip3 install --user sounddevice faster-whisper 2>/dev/null || {
  echo "WARN: faster-whisper install failed — STT stays in keyboard mode until fixed"
}

echo ">>> List audio devices"
arecord -l || true
aplay -l || true

echo "DONE_OK — set input_device in config/voice.yaml after identifying USB mic"
