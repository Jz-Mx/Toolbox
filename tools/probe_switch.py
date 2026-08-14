# -*- coding: utf-8 -*-
"""验证：页面切换正常（各页独立显示/隐藏）。"""
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


def visible(window, page_id):
    return ev_js(window, f"getComputedStyle(document.getElementById('{page_id}')).display !== 'none'")


def probe(window):
    time.sleep(10)
    print("SWITCH:", flush=True)
    print("  dash:", visible(window, "page-dashboard"), flush=True)
    print("  mon:", visible(window, "page-monitor"), flush=True)
    # 切到监控
    ev_js(window, "document.querySelector('[data-page=monitor]').click()", 5)
    time.sleep(1.5)
    print("  after click monitor -> dash:", visible(window, "page-dashboard"), "mon:", visible(window, "page-monitor"), flush=True)
    # 切到工具
    ev_js(window, "document.querySelector('[data-page=tools]').click()", 5)
    time.sleep(1.5)
    print("  after click tools -> mon:", visible(window, "page-monitor"), "tools:", visible(window, "page-tools"), flush=True)
    # 回首页
    ev_js(window, "document.querySelector('[data-page=dashboard]').click()", 5)
    time.sleep(1.5)
    print("  back dash -> dash:", visible(window, "page-dashboard"), "tools:", visible(window, "page-tools"), flush=True)
    print("  dash flex:", ev_js(window, "getComputedStyle(document.getElementById('page-dashboard')).display + ' ' + getComputedStyle(document.getElementById('page-dashboard')).flexDirection"), flush=True)
    print("  detail bottom:", ev_js(window, "(function(){var d=document.querySelector('.detail-panel').getBoundingClientRect();var m=document.querySelector('.main').getBoundingClientRect();return Math.round(m.bottom - d.bottom);})()"), flush=True)
    print("PROBE_SWITCH_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
