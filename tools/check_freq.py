# -*- coding: utf-8 -*-
"""验证 CPU 频率实时波动：负载下观察频率变化。"""
import sys
import threading
import time

sys.path.insert(0, r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent")
from app import TalentAPI


def load():
    end = time.time() + 4
    x = 0
    while time.time() < end:
        for i in range(200000):
            x += i * i
    return x


api = TalentAPI()
print("采样（1 秒间隔，前 3 秒空闲后 4 秒负载）:", flush=True)
vals = []
for i in range(7):
    p = api.get_perf()
    vals.append(p["cpu_freq_mhz"])
    print(f"  t={i}s freq={p['cpu_freq_mhz']}MHz cpu={p['cpu']}%", flush=True)
    if i == 2:
        threading.Thread(target=load, daemon=True).start()
    time.sleep(1)
print("max-min 波动:", max(vals) - min(vals), "MHz", flush=True)
print("WAVE_OK" if max(vals) - min(vals) > 0 else "NO_WAVE", flush=True)
