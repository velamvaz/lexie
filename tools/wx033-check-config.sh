#!/usr/bin/env bash
# WX-033 — Read back config.json from device (no secrets printed)
set -euo pipefail

PORT="${PORT:-$(ls /dev/cu.usb* 2>/dev/null | head -1)}"
if [[ -z "$PORT" ]]; then
  echo "No USB port."
  exit 1
fi

MPY_PYTHON="${LEXIE_PYTHON:-/usr/bin/python3}"

"$MPY_PYTHON" -m mpremote connect "$PORT" exec "
import json
try:
    with open('config.json') as f:
        c = json.load(f)
except OSError:
    print('config_missing')
    raise SystemExit(1)
nets = c.get('networks', [])
print('config_ok', len(nets), 'network(s)', c.get('base_url', ''))
for i, n in enumerate(nets):
    print('ssid', i, n.get('ssid', ''))
print('device_key_set', bool(c.get('device_key')))
"
