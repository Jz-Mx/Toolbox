# -*- coding: utf-8 -*-
"""验证：监控页 CPU 显示详细型号。"""
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
    api = TalentAPI()
    s = api.get_sysinfo()
    print("PY cpu_name:", s.get("cpu_name"), flush=True)
    ev_js(window, "document.querySelector('[data-page=monitor]').click()", 5)
    time.sleep(4)
    print("UI cpu row:", ev_js(window, "document.querySelectorAll('#sysinfoBody tr')[1].querySelector('td:last-child').textContent"), flush=True)
    print("PROBE_CPUNAME_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
