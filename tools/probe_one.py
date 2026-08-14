# -*- coding: utf-8 -*-
"""验证：详情单列竖排（开机/系统合并、磁盘行删除）。"""
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
    print("DETAIL:", flush=True)
    print("  cols:", ev_js(window, "getComputedStyle(document.querySelector('.detail-grid')).gridTemplateColumns"), flush=True)
    print("  rows:", ev_js(window, "[...document.querySelectorAll('.detail-panel .d-item')].map(d => d.querySelector('span').textContent + '=' + d.querySelector('b').textContent).join(' | ')"), flush=True)
    print("  disk gone:", ev_js(window, "!document.getElementById('dDisk') && !document.getElementById('dOs') && !document.getElementById('dUptime')"), flush=True)
    print("PROBE_ONE_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
