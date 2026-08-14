# -*- coding: utf-8 -*-
"""模拟前端：每秒调 get_perf，观察 cpu 值。"""
import sys
import threading
import time

sys.path.insert(0, r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent")
from app import TalentAPI

api = TalentAPI()
print("每秒调用 get_perf 12 次：", flush=True)
for i in range(12):
    p = api.get_perf()
    print(f"  t={i}s cpu={p['cpu']}%", flush=True)
    time.sleep(1)
print("DONE", flush=True)
