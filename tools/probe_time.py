# -*- coding: utf-8 -*-
"""验证：时间只显示年月日星期、详情新格式。"""
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
    time.sleep(10)
    print("TIME:", flush=True)
    print("  heroDate:", ev_js(window, "document.getElementById('heroDate').textContent"), flush=True)
    print("  heroClock gone:", ev_js(window, "!document.getElementById('heroClock')"), flush=True)
    print("  rows:", ev_js(window, "[...document.querySelectorAll('.detail-panel .d-item')].map(d => d.querySelector('span').textContent + '=' + d.querySelector('b').textContent).join(' | ')", 15), flush=True)
    print("PROBE_TIME_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
