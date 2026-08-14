# -*- coding: utf-8 -*-
"""验证睿频探测与前端显示。"""
import os
import sys
import threading
import time

sys.path.insert(0, r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent")

import app

# 启动探测线程（模拟应用启动）
app.start_max_freq_detect()
time.sleep(4)

import webview


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
    time.sleep(8)
    api = app.TalentAPI()
    s = api.get_sysinfo()
    print("PY max:", s.get("cpu_max_mhz"), "model:", s.get("cpu_model"), flush=True)
    print("UI dCpu:", ev_js(window, "document.getElementById('dCpu').textContent"), flush=True)
    print("PROBE_MAX_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = app.TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
