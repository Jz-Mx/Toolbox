# -*- coding: utf-8 -*-
"""验证：内存规格显示与实时频率。"""
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
    api = TalentAPI()
    s = api.get_sysinfo()
    print("PY mem_spec:", s.get("mem_spec"), flush=True)
    p = api.get_perf()
    print("PY freq:", p.get("cpu_freq_mhz"), "mem_used:", p.get("mem_used"), flush=True)

    print("UI:", flush=True)
    print("  dCpu(freq):", ev_js(window, "document.getElementById('dCpu').textContent"), flush=True)
    print("  dMem(used/total):", ev_js(window, "document.getElementById('dMem').textContent"), flush=True)
    print("  dMemSpec:", ev_js(window, "document.getElementById('dMemSpec').textContent"), flush=True)

    # 频率实时性：隔 2 秒再读
    f1 = ev_js(window, "document.getElementById('dCpu').textContent")
    time.sleep(2)
    f2 = ev_js(window, "document.getElementById('dCpu').textContent")
    print("  freq t0:", f1, "t2s:", f2, flush=True)
    print("PROBE_MEM_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
