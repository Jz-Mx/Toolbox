# -*- coding: utf-8 -*-
"""调试：等待探测完成（最多 15 秒）。"""
import sys
import time

sys.path.insert(0, r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent")
import app

app.start_max_freq_detect()
for i in range(15):
    time.sleep(1)
    if app._max_freq_mhz:
        print(f"t={i+1}s max={app._max_freq_mhz}", flush=True)
        break
else:
    print("still 0 after 15s", flush=True)

s = app.TalentAPI().get_sysinfo()
print("sysinfo cpu_max_mhz:", s.get("cpu_max_mhz"), flush=True)
print("DONE", flush=True)
