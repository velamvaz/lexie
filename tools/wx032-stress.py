#!/usr/bin/env python3
"""WX-032 — Monitor serial for LEXIE_E2E stress test results."""
from __future__ import annotations

import argparse
import glob
import re
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import serial
except ImportError:
    print("Install pyserial: pip3 install pyserial", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "project-management" / "logs"

SUMMARY_RE = re.compile(r"LEXIE_E2E: SUMMARY pass=(\d+) fail=(\d+)")
FAIL_RE = re.compile(r"LEXIE_E2E: cycle=(\d+)/(\d+) FAIL stage=(\w+)")
PLAYBACK_OK_RE = re.compile(r"LEXIE_E2E: cycle=(\d+)/(\d+) stage=playback_ok")


def pick_port(explicit: str | None) -> str:
    if explicit:
        return explicit
    ports = sorted(glob.glob("/dev/cu.usb*"))
    if not ports:
        print("No /dev/cu.usb* — plug in board.", file=sys.stderr)
        sys.exit(2)
    return ports[0]


def open_serial(port: str) -> serial.Serial:
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = 115200
    ser.timeout = 0.3
    ser.dtr = False
    ser.rts = False
    try:
        ser.open()
    except serial.SerialException as exc:
        print(f"Cannot open {port}: {exc}", file=sys.stderr)
        sys.exit(2)
    ser.dtr = False
    ser.rts = False
    return ser


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade WX-032 automated E2E stress test")
    parser.add_argument("port", nargs="?", help="Serial port (default: first /dev/cu.usb*)")
    parser.add_argument("--expect", type=int, default=10, help="Required pass count (default: 10)")
    parser.add_argument("--timeout", type=int, default=900, help="Seconds to wait for SUMMARY")
    parser.add_argument("--loop", action="store_true", help="On failure print diagnosis and log path")
    args = parser.parse_args()

    port = pick_port(args.port)
    print(f"Port: {port}  expect={args.expect}  timeout={args.timeout}s")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOG_DIR / f"wx032-stress-{stamp}.txt"

    ser = open_serial(port)
    time.sleep(1.0)

    lines: list[str] = []
    playback_ok = 0
    last_fail: str | None = None
    summary: tuple[int, int] | None = None
    deadline = time.time() + args.timeout

    print(f"Logging to {log_path}")
    print("Waiting for LEXIE_E2E: SUMMARY …")

    with log_path.open("w", encoding="utf-8") as logf:
        while time.time() < deadline:
            chunk = ser.read(4096)
            if not chunk:
                continue
            text = chunk.decode("utf-8", errors="replace")
            logf.write(text)
            logf.flush()

            for raw_line in text.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                lines.append(line)

                if PLAYBACK_OK_RE.search(line):
                    playback_ok += 1
                    print(line)

                m_fail = FAIL_RE.search(line)
                if m_fail:
                    last_fail = line
                    print(line, file=sys.stderr)

                m_sum = SUMMARY_RE.search(line)
                if m_sum:
                    summary = (int(m_sum.group(1)), int(m_sum.group(2)))
                    print(line)
                    break

            if summary is not None:
                break

    ser.close()

    if summary is None:
        print(f"TIMEOUT — no LEXIE_E2E: SUMMARY within {args.timeout}s", file=sys.stderr)
        print(f"Log: {log_path}")
        if last_fail:
            print(f"Last failure: {last_fail}", file=sys.stderr)
        return 2

    passed, failed = summary
    print(f"Result: pass={passed} fail={failed} playback_ok_lines={playback_ok}")
    print(f"Log: {log_path}")

    if failed == 0 and passed >= args.expect:
        print(f"PASS — {passed}/{args.expect} cycles")
        return 0

    if args.loop and last_fail:
        print(f"Diagnosis: {last_fail}", file=sys.stderr)

    print(f"FAIL — need pass={args.expect} fail=0, got pass={passed} fail={failed}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
