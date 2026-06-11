#!/usr/bin/env bash
# WX-028 — Wi-Fi smoke: scan + optional join
# Usage:
#   ./tools/wx028-wifi-smoke.sh                    # scan only
#   ./tools/wx028-wifi-smoke.sh 'MySSID' 'MyPass'  # scan + connect
set -euo pipefail

# MicroPython tools use system Python — not the ESP-IDF venv (no mpremote there).
if [[ -n "${LEXIE_PYTHON:-}" ]]; then
  MPY_PYTHON="$LEXIE_PYTHON"
elif /usr/bin/python3 -m mpremote --version >/dev/null 2>&1; then
  MPY_PYTHON=/usr/bin/python3
else
  echo "mpremote not found. Install: /usr/bin/python3 -m pip install --user mpremote"
  exit 1
fi

PORT="${PORT:-$(ls /dev/cu.usb* 2>/dev/null | head -1)}"
if [[ -z "$PORT" ]]; then
  echo "No USB port."
  exit 1
fi

SSID="${1:-}"
PASSWORD="${2:-}"

"$MPY_PYTHON" -m mpremote connect "$PORT" exec "
import network, time
w = network.WLAN(network.STA_IF)
w.active(True)
nets = w.scan()
print('scan_count', len(nets))
for n in nets[:8]:
    print('ap', n[0].decode())
"

if [[ -n "$SSID" ]]; then
  "$MPY_PYTHON" -m mpremote connect "$PORT" exec "
import network, time
w = network.WLAN(network.STA_IF)
w.active(True)
w.connect('${SSID//\'/\\\'}', '${PASSWORD//\'/\\\'}')
for i in range(20):
    if w.isconnected():
        print('wifi_ok', w.ifconfig())
        break
    time.sleep(0.5)
else:
    print('wifi_fail', w.status())
    raise SystemExit(1)
"
fi
