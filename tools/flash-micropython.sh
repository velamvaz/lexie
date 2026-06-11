#!/usr/bin/env bash
# WX-028 — Flash MicroPython (ESP32-S3 SPIRAM_OCT) to Waveshare board
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$ROOT/firmware/bin/ESP32_GENERIC_S3-SPIRAM_OCT-20250415-v1.25.0.bin"
CHIP=esp32s3

if [[ ! -f "$BIN" ]]; then
  echo "Missing firmware: $BIN"
  echo "Download: https://micropython.org/resources/firmware/ESP32_GENERIC_S3-SPIRAM_OCT-20250415-v1.25.0.bin"
  exit 1
fi

if [[ -n "${1:-}" ]]; then
  PORT="$1"
else
  PORT=$(ls /dev/cu.usb* 2>/dev/null | head -1 || true)
  if [[ -z "$PORT" ]]; then
    echo "No USB port. Plug in board (data cable) and retry."
    exit 1
  fi
fi

echo "=== Flash MicroPython v1.25.0 (SPIRAM_OCT) ==="
echo "Port: $PORT"
python3 -m esptool --chip "$CHIP" -p "$PORT" -b 460800 write_flash 0 "$BIN"
echo ""
echo "Flashed. Now run: ./tools/wx028-check-repl.sh $PORT"
echo "If REPL fails: tap RESET once (do NOT hold BOOT), then retry."
