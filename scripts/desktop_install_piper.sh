#!/usr/bin/env bash
# Install Piper TTS + a natural English voice for desktop/Pi (replaces robotic espeak).
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIPER_DIR="$ROOT/models/piper"
VOICE_DIR="$PIPER_DIR/en_US-lessac-medium"
ARCH="$(uname -m)"

echo "=== Piper TTS install ==="

mkdir -p "$PIPER_DIR"
cd "$PIPER_DIR"

if [[ ! -x "$PIPER_DIR/piper/piper" ]]; then
  case "$ARCH" in
    x86_64)
      URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz"
      ;;
    aarch64|arm64)
      URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz"
      ;;
    *)
      echo "Unsupported arch: $ARCH"
      exit 1
      ;;
  esac
  echo ">>> Downloading Piper ($ARCH)..."
  curl -L "$URL" -o piper.tar.gz
  tar -xzf piper.tar.gz
  rm -f piper.tar.gz
fi

export PATH="$PIPER_DIR/piper:$PATH"

if [[ ! -f "$VOICE_DIR/en_US-lessac-medium.onnx" ]]; then
  echo ">>> Downloading en_US-lessac-medium voice..."
  mkdir -p "$VOICE_DIR"
  curl -L \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx" \
    -o "$VOICE_DIR/en_US-lessac-medium.onnx"
  curl -L \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json" \
    -o "$VOICE_DIR/en_US-lessac-medium.onnx.json"
fi

AMY_DIR="$PIPER_DIR/en_US-amy-medium"
if [[ ! -f "$AMY_DIR/en_US-amy-medium.onnx" ]]; then
  echo ">>> Downloading en_US-amy-medium voice (robot TTS profile)..."
  mkdir -p "$AMY_DIR"
  curl -L \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx" \
    -o "$AMY_DIR/en_US-amy-medium.onnx"
  curl -L \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json" \
    -o "$AMY_DIR/en_US-amy-medium.onnx.json"
fi

MODEL="$VOICE_DIR/en_US-lessac-medium.onnx"
echo ""
echo "Piper binary: $PIPER_DIR/piper/piper"
echo "Voice model:  $MODEL"
echo ""
echo "Add to your shell profile (optional):"
echo "  export PATH=\"$PIPER_DIR/piper:\$PATH\""
echo ""
echo "Desktop demo picks this up automatically when present."
echo "Test: echo 'Hello, I am Companion.' | piper --model '$MODEL' --output_file - | aplay"
