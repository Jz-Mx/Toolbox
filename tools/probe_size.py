# -*- coding: utf-8 -*-
"""验证：提问框元素放大。"""
import os
import sys
import threading
import time

import webview

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app
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
    time.sleep(10)
    print("SIZES:", flush=True)
    print("  title:", ev_js(window, "getComputedStyle(document.querySelector('.daily-title')).fontSize"), flush=True)
    print("  q:", ev_js(window, "getComputedStyle(document.getElementById('dailyQ')).fontSize"), flush=True)
    print("  input font:", ev_js(window, "getComputedStyle(document.getElementById('dailyInput')).fontSize + ' pad=' + getComputedStyle(document.getElementById('dailyInput')).padding"), flush=True)
    print("  send:", ev_js(window, "Math.round(document.getElementById('dailySend').getBoundingClientRect().width) + 'x' + Math.round(document.getElementById('dailySend').getBoundingClientRect().height)"), flush=True)
    print("  star:", ev_js(window, "Math.round(document.getElementById('dailyCheck').getBoundingClientRect().width) + ' font=' + getComputedStyle(document.getElementById('dailyCheck')).fontSize"), flush=True)
    print("PROBE_SZ_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
app.start_max_freq_detect()
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
