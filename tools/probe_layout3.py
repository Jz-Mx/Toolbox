# -*- coding: utf-8 -*-
"""验证：题目居中上移、输入框左下。"""
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
    print("LAYOUT:", flush=True)
    print("  q align:", ev_js(window, "getComputedStyle(document.getElementById('dailyQ')).textAlign + ' alignSelf=' + getComputedStyle(document.getElementById('dailyQ')).alignSelf"), flush=True)
    print("  daily justify:", ev_js(window, "getComputedStyle(document.querySelector('.daily')).justifyContent"), flush=True)
    # 题目位置（框内上移）
    print("  q top offset:", ev_js(window, "(function(){var q=document.getElementById('dailyQ').getBoundingClientRect();var d=document.querySelector('.daily').getBoundingClientRect();return Math.round(q.top - d.top);})()"), flush=True)
    # 输入框左下
    print("  input pos:", ev_js(window, "(function(){var i=document.getElementById('dailyInput').getBoundingClientRect();var d=document.querySelector('.daily').getBoundingClientRect();return 'left=' + Math.round(i.left-d.left) + ' bottom=' + Math.round(d.bottom-i.bottom);})()"), flush=True)
    print("PROBE_L3_DONE", flush=True)


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
