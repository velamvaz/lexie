#!/usr/bin/env bash
# Clone Waveshare screen-less audio demo for WX-036 Phase 1 (playback beeps)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/firmware/wx036-reference/esp32-s3-audio-board-starter"
REPO="https://github.com/rchrd2/esp32-s3-audio-board-starter.git"

mkdir -p "$ROOT/firmware/wx036-reference"

if [[ -d "$DEST/.git" ]]; then
  echo "Already cloned: $DEST"
  cd "$DEST" && git pull --ff-only || true
else
  git clone --depth 1 "$REPO" "$DEST"
fi

echo "Cloned to: $DEST"
echo "Next (after: source ~/esp/esp-idf/export.sh):"
echo "  cd $DEST"
echo "  idf.py set-target esp32s3"
echo "  idf.py build"
echo "  idf.py -p PORT flash monitor"
