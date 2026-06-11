#!/usr/bin/env python3
"""WX-028 — MicroPython REPL check with macOS timing workaround."""
import sys
import time

try:
    import serial
except ImportError:
    print("Install pyserial: pip3 install pyserial")
    sys.exit(1)

PORT = sys.argv[1] if len(sys.argv) > 1 else None
if not PORT:
    import glob
    ports = sorted(glob.glob("/dev/cu.usb*"))
    if not ports:
        print("No /dev/cu.usb* — plug in board with data cable.")
        sys.exit(1)
    PORT = ports[0]

print(f"Port: {PORT}")
print("If this hangs or fails: unplug USB, plug back in (no BOOT), tap RESET, retry.\n")

# Run-mode friendly open (avoid strapping into download mode)
ser = serial.Serial()
ser.port = PORT
ser.baudrate = 115200
ser.timeout = 0.3
ser.dtr = False
ser.rts = False
try:
    ser.open()
except serial.SerialException as e:
    print(f"Cannot open port: {e}")
    print("Try another USB port/cable or unplug-replug the board.")
    sys.exit(1)

ser.dtr = False
ser.rts = False
time.sleep(2.5)  # ESP32-S3 USB CDC needs time after boot on macOS
# Do NOT pulse RTS here — it can re-enter download mode on Waveshare after flash.

# Interrupt any running code
for _ in range(3):
    ser.write(b"\x03")
    time.sleep(0.2)
ser.write(b"\r\n")
time.sleep(0.5)

banner = b""
deadline = time.time() + 5
while time.time() < deadline:
    banner += ser.read(4096)
    if b">>>" in banner or b"MicroPython" in banner:
        break
    time.sleep(0.1)

if banner:
    print(banner.decode("utf-8", "replace")[:500])

if b">>>" not in banner and b"MicroPython" not in banner:
    print("No REPL prompt yet.")
    print("→ Tap RESET once (do NOT hold BOOT), wait 2s, run this script again.")
    ser.close()
    sys.exit(1)

# Enter raw REPL (mpremote protocol)
time.sleep(1)
ser.write(b"\r\x01")
deadline = time.time() + 5
raw = b""
while time.time() < deadline:
    raw += ser.read(4096)
    if b"raw REPL" in raw or b"OK" in raw:
        break
    time.sleep(0.1)

ser.write(b"import sys\r\nprint('lexie_repl_ok', sys.implementation.name, sys.version)\r\n")
ser.write(b"\x04")  # ctrl-D execute
deadline = time.time() + 5
out = b""
while time.time() < deadline:
    chunk = ser.read(4096)
    if chunk:
        out += chunk
    if b"lexie_repl_ok" in out:
        break
    time.sleep(0.1)

ser.write(b"\x02")  # ctrl-B exit raw repl
ser.close()

text = out.decode("utf-8", "replace")
print(text)
if "lexie_repl_ok" in text:
    print("\nREPL OK — WX-028 REPL step passed.")
    sys.exit(0)

print("\nREPL failed. Try: ./tools/flash-micropython.sh then RESET and retry.")
sys.exit(1)
