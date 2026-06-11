#!/usr/bin/env bash
# WX-032 — Build Lexie Waveshare ESP-IDF firmware
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IDF_DIR="${IDF_PATH:-$HOME/esp/esp-idf}"
PROJECT="$ROOT/firmware/lexie-waveshare-idf"

if [[ ! -f "$ROOT/config.local.json" ]]; then
  echo "Run: cp firmware/config.example.json config.local.json && edit secrets"
  exit 1
fi

"$ROOT/tools/wx033-provision-idf.sh" "$ROOT/config.local.json"

export IDF_PATH="$IDF_DIR"
set +u
eval "$(/opt/homebrew/bin/python3.11 "$IDF_PATH/tools/activate.py" --export --shell zsh)"
set -u

cd "$PROJECT"
if [[ ! -f sdkconfig ]]; then
  idf.py set-target esp32s3
fi
rm -f dependencies.lock
idf.py build
echo ""
echo "Build OK. Flash with: ./tools/wx032-flash.sh"
