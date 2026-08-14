# -*- coding: utf-8 -*-
"""验证：强调色折叠按钮展开、详情面板浮动定位与左右切换。"""
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

    print("DETAIL PANEL:", flush=True)
    print("  pos:", ev_js(window, "getComputedStyle(document.getElementById('detailPanel')).position + ' right=' + getComputedStyle(document.getElementById('detailPanel')).right + ' bottom=' + getComputedStyle(document.getElementById('detailPanel')).bottom"), flush=True)
    print("  backdrop-filter:", ev_js(window, "getComputedStyle(document.getElementById('detailPanel')).backdropFilter || getComputedStyle(document.getElementById('detailPanel')).webkitBackdropFilter"), flush=True)
    print("  bg:", ev_js(window, "getComputedStyle(document.getElementById('detailPanel')).backgroundColor"), flush=True)
    print("  data:", ev_js(window, "document.getElementById('dCpu').textContent + ' ' + document.getElementById('dOs').textContent"), flush=True)

    # 切换位置（右下 -> 左下）
    ev_js(window, "document.getElementById('detailPos').click()", 5)
    time.sleep(0.8)
    print("  after click:", ev_js(window, "document.getElementById('detailPanel').classList.contains('pos-left') ? 'LEFT' : 'RIGHT'"), flush=True)
    print("  saved:", ev_js(window, "localStorage.getItem('talent_detail_pos')"), flush=True)
    # 再点回
    ev_js(window, "document.getElementById('detailPos').click()", 5)
    time.sleep(0.6)
    print("  after click2:", ev_js(window, "document.getElementById('detailPanel').classList.contains('pos-left') ? 'LEFT' : 'RIGHT'"), flush=True)

    # 强调色折叠按钮
    ev_js(window, "document.querySelector('[data-page=about]').click()", 5)
    time.sleep(2)
    print("COLOR TOGGLE:", flush=True)
    print("  pop hidden:", ev_js(window, "document.getElementById('colorPop').hidden"), flush=True)
    print("  dot bg:", ev_js(window, "getComputedStyle(document.getElementById('ctDot')).backgroundColor"), flush=True)
    ev_js(window, "document.getElementById('colorToggle').click()", 5)
    time.sleep(0.6)
    print("  pop after click:", ev_js(window, "document.getElementById('colorPop').hidden ? 'HIDDEN' : 'VISIBLE'"), flush=True)
    print("  swatches:", ev_js(window, "document.querySelectorAll('#accentPalette .swatch').length"), flush=True)
    ev_js(window, "document.querySelector('#accentPalette .swatch').click()", 5)
    time.sleep(0.6)
    print("  pop after pick:", ev_js(window, "document.getElementById('colorPop').hidden ? 'HIDDEN' : 'VISIBLE'"), flush=True)
    print("  accent:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()"), flush=True)

    print("PROBE_LAYOUT_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
