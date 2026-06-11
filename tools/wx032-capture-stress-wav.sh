#!/usr/bin/env bash
# One-time: capture stress_phrase.wav for WX-032 automated E2E (16 kHz mono PCM)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/firmware/lexie-waveshare-idf/test_assets/stress_phrase.wav"
WORD="${1:-lumos}"

mkdir -p "$(dirname "$OUT")"
TMP="$(mktemp /tmp/lexie_stress.XXXXXX.aiff)"
trap 'rm -f "$TMP"' EXIT

echo "Synthesizing \"$WORD\" → $OUT"
say -o "$TMP" "$WORD"

if command -v ffmpeg >/dev/null 2>&1; then
  ffmpeg -y -loglevel error -i "$TMP" -ac 1 -ar 16000 "$OUT"
elif command -v afconvert >/dev/null 2>&1; then
  afconvert -f WAVE -d LEI16@16000 -c 1 "$TMP" "$OUT"
else
  echo "Need ffmpeg or afconvert"
  exit 1
fi

echo "Wrote $(wc -c <"$OUT") bytes: $OUT"
echo "Next: ./tools/wx033-provision-idf.sh && ./tools/wx032-build.sh"
