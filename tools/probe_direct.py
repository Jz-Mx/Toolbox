# -*- coding: utf-8 -*-
"""直接检查前端 js_api 返回的完整 perf 数据。"""
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
    time.sleep(8)
    # 前端直接调用并缓存结果
    ev_js(window, "window.pywebview.api.get_perf().then(r => { window.__perf = r; })", 5)
    time.sleep(3)
    print("FRONT PERF:", ev_js(window, "JSON.stringify(window.__perf)"), flush=True)
    print("UI hpCpu:", ev_js(window, "document.getElementById('hpCpu').textContent"), flush=True)
    print("PY:", TalentAPI().get_perf(), flush=True)
    print("PROBE_DIRECT_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
