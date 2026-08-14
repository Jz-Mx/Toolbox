# -*- coding: utf-8 -*-
"""验证：详情信息在首页内显示（纯透明、无浮动、无切换按钮）。"""
import os
import sys
import threading
import time

import webview

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import TalentAPI


def ev_js(window, expr, timeout=10):
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
    print("DETAIL:", flush=True)
    print("  pos:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).position"), flush=True)
    print("  bg:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).backgroundColor"), flush=True)
    print("  parent:", ev_js(window, "document.querySelector('.detail-panel').parentElement.id"), flush=True)
    print("  switch btn exists:", ev_js(window, "!!document.getElementById('detailPos')"), flush=True)
    print("  data:", ev_js(window, "document.getElementById('dCpu').textContent + ' ' + document.getElementById('dMemUse').textContent + ' ' + document.getElementById('dOs').textContent + ' ' + document.getElementById('dGpu').textContent"), flush=True)
    print("  hero after:", ev_js(window, "!!document.querySelector('.detail-panel') && document.querySelector('.dash-grid') ? 'LAYOUT_OK' : 'BAD'"), flush=True)
    print("PROBE_INLINE_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
