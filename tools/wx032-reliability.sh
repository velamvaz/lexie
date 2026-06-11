#!/usr/bin/env bash
# WX-032 — Provision, build, flash, and run 10× automated E2E stress gate
# Usage: ./tools/wx032-reliability.sh [PORT] [--expect N] [--loop]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PORT=""
EXPECT=10
LOOP=""
for arg in "$@"; do
  case "$arg" in
    --loop) LOOP="--loop" ;;
    --expect=*) EXPECT="${arg#*=}" ;;
    --expect)
      ;;
    /dev/*) PORT="$arg" ;;
    *)
      if [[ "$arg" =~ ^[0-9]+$ ]]; then
        EXPECT="$arg"
      fi
      ;;
  esac
done

# Handle --expect as separate arg
args=("$@")
for ((i = 0; i < ${#args[@]}; i++)); do
  if [[ "${args[i]}" == "--expect" && $((i + 1)) -lt ${#args[@]} ]]; then
    EXPECT="${args[i + 1]}"
  fi
done

if [[ -z "$PORT" ]]; then
  PORT="$(ls /dev/cu.usb* 2>/dev/null | head -1 || true)"
fi
if [[ -z "$PORT" ]]; then
  echo "No USB port — pass PORT as first argument"
  exit 1
fi

echo "=== WX-032 reliability gate ==="
echo "Port: $PORT  expect: $EXPECT"

./tools/wx033-provision-idf.sh "${LEXIE_CONFIG:-config.local.json}"
./tools/wx032-build.sh

echo "Flashing (close any open monitor first)…"
./tools/wx032-flash.sh "$PORT"

echo "Tap RESET on the board, then starting stress monitor…"
sleep 3

/usr/bin/python3 ./tools/wx032-stress.py "$PORT" --expect "$EXPECT" $LOOP
