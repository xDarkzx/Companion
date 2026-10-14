#!/usr/bin/env bash
# Download free CC0 robot beeps/boops (Kenney) into companion_face/assets/sfx.
set -eo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/ros2_ws/src/companion_face/assets/sfx"
TMP="$ROOT/assets/sfx_staging"
ZIP="$TMP/kenney_interface.zip"
KENNEY_URL="https://kenney.nl/media/pages/assets/interface-sounds/e537b869c4-1677589129/interface_sounds.zip"

mkdir -p "$OUT" "$TMP"

echo "=== Robot beeps and boops (Kenney CC0) ==="
echo "Output: $OUT"
echo ""

if ! command -v unzip >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y unzip
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  sudo apt-get install -y ffmpeg
fi

echo ">>> Downloading Kenney Interface Sounds (CC0)..."
curl -fsSL "$KENNEY_URL" -o "$ZIP"
unzip -qo "$ZIP" -d "$TMP/kenney"

SRC="$TMP/kenney"
if [[ ! -d "$SRC" ]]; then
  SRC="$(find "$TMP/kenney" -type d -name 'Audio' | head -1)"
fi
if [[ -z "$SRC" ]] || [[ ! -d "$SRC" ]]; then
  SRC="$(find "$TMP/kenney" -type f -name '*.ogg' | head -1 | xargs dirname)"
fi

_to_wav() {
  local src="$1"
  local dest="$2"
  if [[ -f "$src" ]]; then
    ffmpeg -y -loglevel error -i "$src" -ac 1 -ar 22050 "$dest"
    echo "    $dest"
  fi
}

echo ">>> Mapping UI bleeps to robot SFX keys..."
_to_wav "$SRC/confirmation_001.ogg" "$OUT/confirm.wav"
_to_wav "$SRC/select_001.ogg" "$OUT/listen.wav"
_to_wav "$SRC/scroll_001.ogg" "$OUT/think.wav"
_to_wav "$SRC/error_001.ogg" "$OUT/alert.wav"
_to_wav "$SRC/bong_001.ogg" "$OUT/happy.wav"
_to_wav "$SRC/pluck_001.ogg" "$OUT/surprise.wav"
_to_wav "$SRC/tick_001.ogg" "$OUT/wake.wav"

# Keep Kenney ogg as fallbacks for sfx_bank filename lookup
cp -f "$SRC/select_001.ogg" "$OUT/select_001.ogg" 2>/dev/null || true
cp -f "$SRC/scroll_001.ogg" "$OUT/scroll_001.ogg" 2>/dev/null || true
cp -f "$SRC/confirmation_001.ogg" "$OUT/confirmation_001.ogg" 2>/dev/null || true
cp -f "$SRC/error_001.ogg" "$OUT/error_001.ogg" 2>/dev/null || true

rm -rf "$TMP"
echo ""
echo "Done. Rebuild face package or restart demo to load new SFX."
