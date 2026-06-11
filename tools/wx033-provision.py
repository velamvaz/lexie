#!/usr/bin/env python3
"""WX-033 — Validate and write config.json to MicroPython flash over USB."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

MAX_NETWORKS = 3


def find_mpy_python() -> str:
    if env := __import__("os").environ.get("LEXIE_PYTHON"):
        return env
    for candidate in ("/usr/bin/python3", sys.executable):
        try:
            subprocess.run(
                [candidate, "-m", "mpremote", "--version"],
                capture_output=True,
                check=True,
            )
            return candidate
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    print("mpremote not found. Install: /usr/bin/python3 -m pip install --user mpremote")
    sys.exit(1)


def validate_config(data: Any) -> dict:
    if not isinstance(data, dict):
        raise ValueError("config root must be a JSON object")

    for key in ("networks", "base_url", "device_key"):
        if key not in data:
            raise ValueError(f"missing required key: {key}")

    networks = data["networks"]
    if not isinstance(networks, list) or not (1 <= len(networks) <= MAX_NETWORKS):
        raise ValueError(f"networks must be a list of 1–{MAX_NETWORKS} entries")

    for i, net in enumerate(networks):
        if not isinstance(net, dict):
            raise ValueError(f"networks[{i}] must be an object")
        for field in ("ssid", "password"):
            if field not in net or not str(net[field]).strip():
                raise ValueError(f"networks[{i}] missing non-empty {field}")

    base_url = str(data["base_url"]).strip()
    if base_url.endswith("/"):
        raise ValueError("base_url must not have a trailing slash")
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("base_url must be https://host (no path)")

    device_key = str(data["device_key"]).strip()
    if not device_key or device_key.startswith("REPLACE"):
        raise ValueError("device_key must be set (from 1Password — not the example placeholder)")

    return {
        "networks": [
            {"ssid": str(n["ssid"]), "password": str(n["password"])} for n in networks
        ],
        "base_url": base_url,
        "device_key": device_key,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} path/to/config.local.json")
        print("Copy firmware/config.example.json → config.local.json and fill in real values.")
        return 1

    config_path = Path(sys.argv[1]).expanduser().resolve()
    if not config_path.is_file():
        print(f"Not found: {config_path}")
        return 1

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        config = validate_config(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Invalid config: {exc}")
        return 1

    port = __import__("os").environ.get("PORT")
    if not port:
        import glob

        ports = sorted(glob.glob("/dev/cu.usb*"))
        if not ports:
            print("No USB port. Plug in board and retry.")
            return 1
        port = ports[0]

    mpy_python = find_mpy_python()
    tmp = config_path.parent / ".wx033-config-upload.json"
    tmp.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    print(f"Port: {port}")
    print(f"Networks: {len(config['networks'])} profile(s)")
    print(f"base_url: {config['base_url']}")
    print("Writing config.json to device (secrets not printed)...")

    try:
        subprocess.run(
            [
                mpy_python,
                "-m",
                "mpremote",
                "connect",
                port,
                "cp",
                str(tmp),
                ":config.json",
            ],
            check=True,
        )
    except subprocess.CalledProcessError:
        print("Upload failed. Close serial monitor, tap RESET, retry.")
        return 1
    finally:
        tmp.unlink(missing_ok=True)

    verify_script = """
import json
with open("config.json") as f:
    c = json.load(f)
print("config_ok", len(c["networks"]), c["base_url"])
""".strip()

    try:
        subprocess.run(
            [mpy_python, "-m", "mpremote", "connect", port, "exec", verify_script],
            check=True,
        )
    except subprocess.CalledProcessError:
        print("Wrote file but verify read failed — try: ./tools/wx033-check-config.sh")
        return 1

    print("\nWX-033 provision OK — config.json on device.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
