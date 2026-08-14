# -*- coding: utf-8 -*-
"""排查：get_perf 连续调用观察 cpu 值（含负载测试）。"""
import sys
import threading
import time

sys.path.insert(0, r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent")
from app import TalentAPI


def load():
    end = time.time() + 3
    x = 0
    while time.time() < end:
        for i in range(300000):
            x += i
    return x


api = TalentAPI()
print("前 3 秒空闲，后 3 秒负载：", flush=True)
for i in range(6):
    t0 = time.time()
    p = api.get_perf()
    dt = time.time() - t0
    print(f"  t={i}s cpu={p['cpu']}% freq={p['cpu_freq_mhz']} 耗时={dt:.2f}s", flush=True)
    if i == 2:
        threading.Thread(target=load, daemon=True).start()
    time.sleep(1)
print("DONE", flush=True)
