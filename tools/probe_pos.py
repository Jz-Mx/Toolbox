# -*- coding: utf-8 -*-
"""验证：详情固定左下角。"""
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
    print("DETAIL POS:", flush=True)
    print("  position:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).position"), flush=True)
    print("  left:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).left"), flush=True)
    print("  bottom:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).bottom"), flush=True)
    print("  bg:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).backgroundColor"), flush=True)
    print("  parent:", ev_js(window, "document.querySelector('.detail-panel').parentElement.tagName"), flush=True)
    print("  data:", ev_js(window, "document.getElementById('dCpu').textContent + ' ' + document.getElementById('dDiskUse').textContent.slice(0, 20)"), flush=True)
    # 切到其他页面看是否仍在（body 级 fixed）
    ev_js(window, "document.querySelector('[data-page=monitor]').click()", 5)
    time.sleep(2)
    print("  visible on monitor:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).display !== 'none'"), flush=True)
    print("PROBE_POS_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
