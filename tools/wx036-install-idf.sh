#!/usr/bin/env bash
# One-time ESP-IDF v5.4.1 install for esp32s3 (WX-036)
set -euo pipefail

IDF_DIR="${IDF_PATH:-$HOME/esp/esp-idf}"
IDF_BRANCH=v5.4.1

echo "=== WX-036: ESP-IDF install ==="
echo "Target dir: $IDF_DIR"
echo "This may take 15–30 minutes on first run."
echo ""

if [[ ! -d "$IDF_DIR/.git" ]]; then
  mkdir -p "$(dirname "$IDF_DIR")"
  git clone -b "$IDF_BRANCH" --recursive --depth 1 \
    https://github.com/espressif/esp-idf.git "$IDF_DIR"
fi

cd "$IDF_DIR"
git submodule update --init --depth 1 || true
./install.sh esp32s3

echo ""
echo "Done. Each new shell:"
echo "  source $IDF_DIR/export.sh"
echo "Then: ./tools/wx036-clone-demo.sh && cd firmware/wx036-reference/esp32-s3-audio-board-starter && idf.py build"
