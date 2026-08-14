# -*- coding: utf-8 -*-
"""验证：输入栏贴底（距底=距左 10px）、星星同排不重叠。"""
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
    print("POS:", flush=True)
    print("  input left/bottom:", ev_js(window, "(function(){var i=document.getElementById('dailyInput').getBoundingClientRect();var d=document.querySelector('.daily').getBoundingClientRect();return 'left=' + Math.round(i.left-d.left) + ' bottom=' + Math.round(d.bottom-i.bottom);})()"), flush=True)
    print("  star bottom:", ev_js(window, "(function(){var s=document.getElementById('dailyCheck').getBoundingClientRect();var d=document.querySelector('.daily').getBoundingClientRect();return Math.round(d.bottom-s.bottom);})()"), flush=True)
    print("  overlap:", ev_js(window, "(function(){var i=document.getElementById('dailyInput').getBoundingClientRect();var s=document.getElementById('dailyCheck').getBoundingClientRect();return i.right < s.left ? 'NO' : 'YES';})()"), flush=True)
    print("PROBE_ALIGN_DONE", flush=True)


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
