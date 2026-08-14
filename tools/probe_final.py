# -*- coding: utf-8 -*-
"""验证：详情卡数据、图表框、24 色盘、页面切换（无 opacity 动画）。"""
import os
import sys
import threading
import time

import webview

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import TalentAPI


def ev_js(window, expr, timeout=10):
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
    print("DETAIL:", flush=True)
    print("  rows:", ev_js(window, "[...document.querySelectorAll('.detail-card .d-item')].map(d => d.textContent.trim()).join(' | ')", 15), flush=True)

    # 图表框
    ev_js(window, "document.querySelector('[data-page=monitor]').click()", 5)
    time.sleep(3)
    print("CHART:", flush=True)
    print("  canvas bg:", ev_js(window, "getComputedStyle(document.getElementById('chartCpu')).backgroundColor"), flush=True)
    print("  canvas border:", ev_js(window, "getComputedStyle(document.getElementById('chartCpu')).borderTopWidth"), flush=True)

    # 色盘
    ev_js(window, "document.querySelector('[data-page=about]').click()", 5)
    time.sleep(2)
    print("PALETTE:", flush=True)
    print("  swatches:", ev_js(window, "document.querySelectorAll('#accentPalette .swatch').length"), flush=True)

    # 页面切换动画（无 opacity）
    print("ANIM:", flush=True)
    print("  pageIn keyframes:", ev_js(window, "document.styleSheets && [...document.styleSheets].map(s => { try { return [...s.cssRules].filter(r => r.name === 'pageIn').map(r => r.cssText).join('') } catch(e) { return '' } }).join('')"), flush=True)

    # 切回首页确认详情卡数值
    ev_js(window, "document.querySelector('[data-page=dashboard]').click()", 5)
    time.sleep(2)
    print("BACK:", flush=True)
    print("  detail cpu:", ev_js(window, "document.getElementById('dCpu').textContent + ' mem ' + document.getElementById('dMemUse').textContent + ' os ' + document.getElementById('dOs').textContent"), flush=True)

    print("PROBE_FINAL_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
