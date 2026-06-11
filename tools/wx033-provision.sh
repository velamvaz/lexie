#!/usr/bin/env bash
# WX-033 — Write config.json to MicroPython flash (WX-025 shape)
# Usage:
#   cp firmware/config.example.json config.local.json   # edit with real values
#   ./tools/wx033-provision.sh config.local.json
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 path/to/config.local.json"
  echo ""
  echo "  cp firmware/config.example.json config.local.json"
  echo "  # edit SSIDs, passwords, device_key from 1Password"
  echo "  $0 config.local.json"
  exit 1
fi

MPY_PYTHON="${LEXIE_PYTHON:-/usr/bin/python3}"
exec "$MPY_PYTHON" "$ROOT/tools/wx033-provision.py" "$1"
