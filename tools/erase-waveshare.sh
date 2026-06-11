#!/usr/bin/env bash
# WX-035 — Full flash erase for Waveshare ESP32-S3-AUDIO-Board
set -euo pipefail

CHIP=esp32s3

if [[ -n "${1:-}" ]]; then
  PORT="$1"
else
  # Prefer USB modem/serial devices; skip Bluetooth
  PORT=$(ls /dev/cu.usb* 2>/dev/null | head -1 || true)
  if [[ -z "$PORT" ]]; then
    echo "No /dev/cu.usb* port found."
    echo "Plug in the board with a USB-C DATA cable, then run:"
    echo "  ls /dev/cu.usb*"
    echo "  $0 /dev/cu.usbmodemXXX"
    exit 1
  fi
fi

echo "=== Lexie WX-035: erase flash ==="
echo "Chip:  $CHIP"
echo "Port:  $PORT"
echo ""
echo "If this fails, hold BOOT, tap RESET, release BOOT, run again."
echo ""

python3 -m esptool --chip "$CHIP" -p "$PORT" erase_flash

echo ""
echo "Done. Vendor firmware erased. Safe next step: WX-028 (flash Lexie smoke image)."
echo "Do NOT join Wi-Fi until Lexie firmware is flashed."
