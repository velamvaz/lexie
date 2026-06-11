#!/usr/bin/env bash
# WX-028 — Confirm MicroPython REPL over USB
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${1:-$(ls /dev/cu.usb* 2>/dev/null | head -1 || true)}"
# System Python — avoid ESP-IDF venv when `python3` points there.
MPY_PYTHON="${LEXIE_PYTHON:-/usr/bin/python3}"
exec "$MPY_PYTHON" "$ROOT/tools/wx028-check-repl.py" ${PORT:+"$PORT"}
