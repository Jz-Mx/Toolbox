# -*- coding: utf-8 -*-
"""验证：天气图标（苹果风格 SVG）显示。"""
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
    api = TalentAPI()
    w = api.get_weather()
    print("PY weather:", w, flush=True)
    print("UI:", flush=True)
    print("  has svg:", ev_js(window, "!!document.querySelector('#heroWeather svg')"), flush=True)
    print("  icon size:", ev_js(window, "(function(){var s=document.querySelector('#heroWeather svg');return s?s.getAttribute('width'):'none';})()"), flush=True)
    print("  text:", ev_js(window, "document.querySelector('#heroWeather .hw-text') ? document.querySelector('#heroWeather .hw-text').textContent : 'none'"), flush=True)
    print("PROBE_WICON_DONE", flush=True)


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
