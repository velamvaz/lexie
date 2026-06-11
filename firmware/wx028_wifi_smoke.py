# WX-028 — Wi-Fi smoke test (run on device via mpremote)
# Host: mpremote connect PORT run firmware/wx028_wifi_smoke.py
# Or edit SSID/PASS below and: mpremote connect PORT exec "exec(open('firmware/wx028_wifi_smoke.py').read())"

import network
import time

SSID = ""  # optional: your test AP name
PASSWORD = ""  # optional: Wi-Fi password

w = network.WLAN(network.STA_IF)
w.active(True)

print("scan...")
for ap in w.scan()[:10]:
    print(" ap:", ap[0].decode())

if SSID:
    print("connecting", SSID)
    w.connect(SSID, PASSWORD)
    for _ in range(30):
        if w.isconnected():
            print("wifi_ok", w.ifconfig())
            break
        time.sleep(0.5)
    else:
        print("wifi_fail status", w.status())
else:
    print("scan_only_ok (set SSID/PASS for join test)")
