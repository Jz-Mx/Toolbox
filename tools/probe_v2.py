# -*- coding: utf-8 -*-
"""验证精简版首页 + 关于页外观面板。"""
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
    print("DASH:", flush=True)
    print("  stat cards:", ev_js(window, "document.querySelectorAll('.stat-card').length"), flush=True)
    print("  quick btns:", ev_js(window, "document.querySelectorAll('.quick').length"), flush=True)
    print("  hero params:", ev_js(window, "document.getElementById('hpCpu').textContent + ' ' + document.getElementById('hpMem').textContent + ' ' + document.getElementById('hpDisk').textContent + ' ' + document.getElementById('hpNet').textContent + ' ' + document.getElementById('hpPing').textContent"), flush=True)
    print("  accent:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()"), flush=True)

    # 关于页外观面板
    ev_js(window, "document.querySelector('[data-page=about]').click()", 5)
    time.sleep(2)
    print("ABOUT:", flush=True)
    print("  appearance:", ev_js(window, "!!document.querySelector('.appearance')"), flush=True)
    print("  palette:", ev_js(window, "document.querySelectorAll('#accentPalette .swatch').length"), flush=True)
    print("  pick:", ev_js(window, "document.getElementById('accentPick').value"), flush=True)
    print("  reset btn:", ev_js(window, "!!document.getElementById('btnAccentReset')"), flush=True)
    print("  qq:", ev_js(window, "document.getElementById('qqText').textContent"), flush=True)

    # 修改强调色
    ev_js(window, "document.getElementById('accentPick').value = '#10b981'; document.getElementById('accentPick').dispatchEvent(new Event('input'))", 5)
    time.sleep(1)
    print("  accent changed:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()"), flush=True)
    print("  saved:", ev_js(window, "localStorage.getItem('talent_theme')"), flush=True)

    # 导航项数
    print("NAV:", ev_js(window, "document.querySelectorAll('.nav-item').length"), flush=True)

    print("PROBE_V2_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
