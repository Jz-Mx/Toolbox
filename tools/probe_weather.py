# -*- coding: utf-8 -*-
"""验证：详情频率显示 + hero 天气。"""
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
    print("FREQ:", flush=True)
    print("  dCpu:", ev_js(window, "document.getElementById('dCpu').textContent"), flush=True)
    print("  hpCpu:", ev_js(window, "document.getElementById('hpCpu').textContent"), flush=True)
    print("  perf freq:", ev_js(window, "API.hasNative ? 'native' : 'mock'"), flush=True)
    # 后端直接验证
    api = TalentAPI()
    p = api.get_perf()
    print("  py freq mhz:", p.get("cpu_freq_mhz"), flush=True)
    w = api.get_weather()
    print("  py weather:", w, flush=True)

    time.sleep(3)
    print("WEATHER UI:", flush=True)
    print("  heroWeather:", ev_js(window, "document.getElementById('heroWeather').textContent"), flush=True)
    print("  weather elem:", ev_js(window, "!!document.getElementById('heroWeather')"), flush=True)
    print("  hero flex:", ev_js(window, "getComputedStyle(document.querySelector('.hero')).display"), flush=True)
    print("PROBE_W_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
