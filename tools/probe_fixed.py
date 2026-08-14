# -*- coding: utf-8 -*-
"""验证：详情固定首页内（文档流，非浮动）。"""
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
    print("  parent:", ev_js(window, "document.querySelector('.detail-panel').parentElement.id"), flush=True)
    print("  position:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).position"), flush=True)
    print("  bg:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).backgroundColor"), flush=True)
    print("  data:", ev_js(window, "document.getElementById('dCpu').textContent + ' | ' + document.getElementById('dNet').textContent"), flush=True)
    # 切到监控页，详情应隐藏（首页专属）
    ev_js(window, "document.querySelector('[data-page=monitor]').click()", 5)
    time.sleep(2)
    print("  on monitor:", ev_js(window, "!!document.querySelector('.detail-panel') && document.querySelector('.detail-panel').offsetParent === null"), flush=True)
    print("PROBE_FIXED_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
