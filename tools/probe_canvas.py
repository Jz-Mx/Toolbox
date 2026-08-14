# -*- coding: utf-8 -*-
"""验证：CPU/内存曲线 canvas 尺寸与基准。"""
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
    ev_js(window, "document.querySelector('[data-page=monitor]').click()", 5)
    time.sleep(4)
    print("CANVAS:", flush=True)
    print("  cpu size:", ev_js(window, "document.getElementById('chartCpu').clientWidth + 'x' + document.getElementById('chartCpu').clientHeight"), flush=True)
    print("  mem size:", ev_js(window, "document.getElementById('chartMem').clientWidth + 'x' + document.getElementById('chartMem').clientHeight"), flush=True)
    print("  cpu css h:", ev_js(window, "getComputedStyle(document.getElementById('chartCpu')).height"), flush=True)
    print("  mem css h:", ev_js(window, "getComputedStyle(document.getElementById('chartMem')).height"), flush=True)
    print("  cpu data:", ev_js(window, "Monitor ? 'module' : 'n/a'"), flush=True)
    print("PROBE_CANVAS_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
