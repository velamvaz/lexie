#!/usr/bin/env bash
# WX-033 — Stage config.json into Lexie ESP-IDF SPIFFS image (before build/flash)
# Usage: ./tools/wx033-provision-idf.sh [path/to/config.local.json]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${1:-$ROOT/config.local.json}"
DEST="$ROOT/firmware/lexie-waveshare-idf/spiffs_image/config.json"

if [[ ! -f "$CFG" ]]; then
  echo "Missing $CFG"
  echo "  cp firmware/config.example.json config.local.json"
  echo "  # edit with Wi-Fi + device_key from 1Password"
  exit 1
fi

/usr/bin/python3 -c "
import json, sys
path = sys.argv[1]
try:
    json.load(open(path))
except json.JSONDecodeError as e:
    print(f'Invalid JSON in {path}: {e}')
    print('Common fix: remove trailing comma after last item in networks[]')
    sys.exit(1)
" "$CFG"
STRESS_WAV="$ROOT/firmware/lexie-waveshare-idf/test_assets/stress_phrase.wav"
SPIFFS_DIR="$ROOT/firmware/lexie-waveshare-idf/spiffs_image"

mkdir -p "$SPIFFS_DIR"
cp "$CFG" "$DEST"

if [[ ! -f "$STRESS_WAV" ]]; then
  echo "Missing stress WAV: $STRESS_WAV"
  echo "  ./tools/wx032-capture-stress-wav.sh lumos"
  exit 1
fi
cp "$STRESS_WAV" "$SPIFFS_DIR/stress_phrase.wav"

echo "Staged SPIFFS config: $DEST"
echo "Staged SPIFFS stress WAV: $SPIFFS_DIR/stress_phrase.wav"
echo "Next: ./tools/wx032-build.sh && ./tools/wx032-flash.sh"
