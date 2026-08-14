# -*- coding: utf-8 -*-
"""验证：详情固定在首页底部（flex margin-top auto）。"""
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
    print("LAYOUT:", flush=True)
    print("  page flex:", ev_js(window, "getComputedStyle(document.getElementById('page-dashboard')).display + ' ' + getComputedStyle(document.getElementById('page-dashboard')).flexDirection"), flush=True)
    print("  detail marginTop:", ev_js(window, "getComputedStyle(document.querySelector('.detail-panel')).marginTop"), flush=True)
    # 位置：详情底部 vs 窗口底部
    print("  detail bottom offset:", ev_js(window, "(function(){var d=document.querySelector('.detail-panel').getBoundingClientRect();var m=document.querySelector('.main').getBoundingClientRect();return Math.round(m.bottom - d.bottom);})()"), flush=True)
    print("  page height:", ev_js(window, "Math.round(document.getElementById('page-dashboard').getBoundingClientRect().height) + ' / main ' + Math.round(document.querySelector('.main').getBoundingClientRect().height)"), flush=True)
    print("PROBE_BOTTOM_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
