#!/usr/bin/env bash
# Create .venv with Python 3.11+ and install lexie-server in editable mode with dev deps.
set -euo pipefail
cd "$(dirname "$0")/.."

pick_python() {
  for cmd in python3.13 python3.12 python3.11 \
    /opt/homebrew/bin/python3.13 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.11 \
    /usr/local/bin/python3.12 /usr/local/bin/python3.11; do
    if command -v "$cmd" &>/dev/null || [ -x "$cmd" ]; then
      ver=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
      major=${ver%%.*}
      minor=${ver#*.}
      if [ "${major:-0}" -eq 3 ] && [ "${minor:-0}" -ge 11 ]; then
        echo "$cmd"
        return 0
      fi
    fi
  done
  return 1
}

PY=$(pick_python) || {
  echo "No Python 3.11+ found (tried PATH + /opt/homebrew + /usr/local)." >&2
  echo "Install one of:" >&2
  echo "  - https://www.python.org/downloads/ (macOS installer; ensure 'Add to PATH')" >&2
  echo "  - brew install python@3.11   (then: export PATH=\"/opt/homebrew/opt/python@3.11/bin:\$PATH\")" >&2
  exit 1
}

echo "Using $($PY --version) at $(command -v "$PY")"
"$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev]"
echo "OK. Activate with: source .venv/bin/activate"
