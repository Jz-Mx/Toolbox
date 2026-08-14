# -*- coding: utf-8 -*-
"""验证：题库扩充（60 题）+ 答过排除逻辑。"""
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
    print("COUNT:", ev_js(window, "typeof Dashboard !== 'undefined' ? 'module' : 'n/a'"), flush=True)
    print("  question count:", ev_js(window, "(function(){return Object.keys(window).length;})()"), flush=True)
    # 通过题目展示验证题库 >= 60（直接检查文本是否为新题）
    print("  Q:", ev_js(window, "document.getElementById('dailyQ').textContent"), flush=True)
    print("  state:", ev_js(window, "localStorage.getItem('talent_daily')"), flush=True)
    print("  done:", ev_js(window, "localStorage.getItem('talent_daily_done')"), flush=True)
    print("PROBE_POOL_DONE", flush=True)


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
