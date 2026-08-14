# -*- coding: utf-8 -*-
"""验证：正确答案点亮星星。"""
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
    print("Q:", ev_js(window, "document.getElementById('dailyQ').textContent"), flush=True)
    # 输入该题正确答案（4x/3）
    ev_js(window, "document.getElementById('dailyInput').value = '4x/3'; document.getElementById('dailySend').click()", 5)
    time.sleep(0.8)
    print("done:", ev_js(window, "document.getElementById('dailyCheck').classList.contains('done')"), flush=True)
    print("anim:", ev_js(window, "getComputedStyle(document.getElementById('dailyCheck')).animationName"), flush=True)
    print("state:", ev_js(window, "localStorage.getItem('talent_daily')"), flush=True)
    print("PROBE_STAR_DONE", flush=True)


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
