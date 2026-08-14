# -*- coding: utf-8 -*-
"""前端连续采样 get_perf 的 cpu（5 次，每秒 1 次）。"""
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
    time.sleep(8)
    # 前端串行采样 5 次（每次间隔 1 秒）
    ev_js(window, """
      window.__cpus = [];
      (function loop(i) {
        if (i >= 5) return;
        window.pywebview.api.get_perf().then(r => { window.__cpus.push(r.cpu); setTimeout(() => loop(i + 1), 1000); });
      })(0);
    """, 5)
    time.sleep(8)
    print("FRONT cpus:", ev_js(window, "JSON.stringify(window.__cpus)"), flush=True)
    print("UI hpCpu:", ev_js(window, "document.getElementById('hpCpu').textContent"), flush=True)
    print("PROBE_SAMPLE_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
app.start_max_freq_detect()  # 启动后台采样线程
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
