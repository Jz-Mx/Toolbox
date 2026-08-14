# -*- coding: utf-8 -*-
"""验证：网络合并行（↓下行 ↑上行 延迟）。"""
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
    print("NET:", flush=True)
    print("  dNet:", ev_js(window, "document.getElementById('dNet').textContent"), flush=True)
    print("  old ids gone:", ev_js(window, "!document.getElementById('dDown') && !document.getElementById('dUp') && !document.getElementById('dPing')"), flush=True)
    print("  items count:", ev_js(window, "document.querySelectorAll('.detail-grid .d-item').length"), flush=True)
    print("PROBE_NET_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
