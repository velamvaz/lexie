#!/usr/bin/env bash
# WX-032 — Flash Lexie firmware to Waveshare board
# Usage:
#   ./tools/wx032-flash.sh [PORT]           # flash only
#   ./tools/wx032-flash.sh [PORT] monitor   # flash + serial monitor
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IDF_DIR="${IDF_PATH:-$HOME/esp/esp-idf}"
PROJECT="$ROOT/firmware/lexie-waveshare-idf"

PORT="${1:-}"
MONITOR="${2:-}"
if [[ "$PORT" == "monitor" ]]; then
  MONITOR=monitor
  PORT=""
fi

if [[ -z "$PORT" ]]; then
  PORT=$(ls /dev/cu.usb* 2>/dev/null | head -1 || true)
fi

if [[ -z "$PORT" ]]; then
  echo "No USB port. Plug in board (data cable) and retry."
  exit 1
fi

export IDF_PATH="$IDF_DIR"
set +u
eval "$(/opt/homebrew/bin/python3.11 "$IDF_PATH/tools/activate.py" --export --shell bash)"
set -u

cd "$PROJECT"
echo "Flashing to $PORT …"
if ! idf.py -p "$PORT" flash; then
  echo ""
  echo "Flash failed. Try:"
  echo "  1. Close any serial monitor / REPL on this port"
  echo "  2. Unplug USB, wait 2s, replug"
  echo "  3. Tap RESET (don't hold BOOT)"
  echo "  4. Retry: ./tools/wx032-flash.sh $PORT"
  exit 1
fi

echo "Flash OK. Tap RESET once, then:"
if [[ "$MONITOR" == "monitor" ]]; then
  idf.py -p "$PORT" monitor
else
  echo "  ./tools/wx032-flash.sh $PORT monitor"
fi
