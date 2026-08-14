# -*- coding: utf-8 -*-
"""验证：CPU 型号 + 实时频率显示（1 秒刷新）。"""
import os
import sys
import threading
import time

import webview

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import TalentAPI


def ev_js(window, expr, timeout=12):
    result = {"done": False, "val": None, "err": None}

    def work():
        try:
            result["val"] = window.evaluate_js(expr)
            result["done"] = True
        except Exception as e:
            result["err"] = repr(e)
            result["done"] = True

    t = threading.Thread(target=work, daemon=True)
    t.start()
    t.join(timeout)
    if not result["done"]:
        return "TIMEOUT"
    if result["err"]:
        return "EV_ERR: " + result["err"]
    return result["val"]


def probe(window):
    time.sleep(9)
    api = TalentAPI()
    s = api.get_sysinfo()
    print("PY cpu_model:", s.get("cpu_model"), flush=True)

    print("UI:", flush=True)
    print("  label:", ev_js(window, "document.querySelector('#page-dashboard .d-item span').textContent"), flush=True)
    print("  dCpu t0:", ev_js(window, "document.getElementById('dCpu').textContent"), flush=True)
    time.sleep(2)
    print("  dCpu t2s:", ev_js(window, "document.getElementById('dCpu').textContent"), flush=True)
    time.sleep(1)
    print("  dCpu t3s:", ev_js(window, "document.getElementById('dCpu').textContent"), flush=True)
    print("PROBE_CPU_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
