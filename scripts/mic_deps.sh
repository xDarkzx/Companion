#!/usr/bin/env bash
# Shared helpers for mic/STT Python dependencies (WSL desktop).
# Root + pip --user breaks imports; use system install with --break-system-packages.

mic_deps_import_ok() {
  python3 -c "import faster_whisper, sounddevice" 2>/dev/null
}

mic_apt_audio_libs() {
  sudo apt-get install -y libportaudio2
  # Ubuntu 24.04+ renamed libasound2 -> libasound2t64
  if apt-cache show libasound2t64 &>/dev/null; then
    sudo apt-get install -y libasound2t64
  else
    sudo apt-get install -y libasound2
  fi
}

mic_deps_install() {
  echo ">>> Installing mic/STT Python packages (system site, for ros2 python3)..."
  sudo apt-get update
  mic_apt_audio_libs
  # Root ignores --user site; install into system paths (not /root/.local).
  # Do not reinstall numpy/setuptools — keep Ubuntu/ROS system versions.
  python3 -m pip install --break-system-packages --ignore-installed \
    faster-whisper sounddevice
  if ! mic_deps_import_ok; then
    echo "ERROR: faster-whisper/sounddevice still not importable by python3."
    python3 -c "import faster_whisper, sounddevice" 2>&1 || true
    return 1
  fi
  echo ">>> Mic/STT deps OK for $(python3 -c 'import sys; print(sys.executable)')"
  return 0
}
