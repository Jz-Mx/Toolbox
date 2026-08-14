# -*- coding: utf-8 -*-
"""验证：提问框布局（输入框缩短透明/发送独立/题目靠左）。"""
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
    print("  input w:", ev_js(window, "Math.round(document.getElementById('dailyInput').getBoundingClientRect().width) + 'px maxWidth=' + getComputedStyle(document.getElementById('dailyInput')).maxWidth"), flush=True)
    print("  input bg:", ev_js(window, "getComputedStyle(document.getElementById('dailyInput')).backgroundColor"), flush=True)
    print("  send pos:", ev_js(window, "(function(){var i=document.getElementById('dailyInput').getBoundingClientRect();var s=document.getElementById('dailySend').getBoundingClientRect();return 'send left - input right = ' + Math.round(s.left - i.right) + 'px (overlap if <0)';})()"), flush=True)
    print("  q align:", ev_js(window, "getComputedStyle(document.getElementById('dailyQ')).textAlign + ' alignSelf=' + getComputedStyle(document.getElementById('dailyQ')).alignSelf"), flush=True)
    print("  send bg:", ev_js(window, "getComputedStyle(document.getElementById('dailySend')).backgroundImage !== 'none' ? 'GRAD' : getComputedStyle(document.getElementById('dailySend')).backgroundColor"), flush=True)
    print("PROBE_LAYOUT2_DONE", flush=True)


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
