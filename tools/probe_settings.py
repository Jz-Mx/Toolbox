# -*- coding: utf-8 -*-
"""验证主题系统：强调色提取/应用、设置页、hero 参数行。"""
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
    print("THEME:", flush=True)
    print("  accent:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()"), flush=True)
    print("  accent2:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--accent2').trim()"), flush=True)
    print("  nav-accent:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--nav-accent').trim()"), flush=True)
    print("  saved:", ev_js(window, "localStorage.getItem('talent_theme')"), flush=True)
    print("  hero params:", ev_js(window, "document.getElementById('hpCpu').textContent + ' / ' + document.getElementById('hpMem').textContent + ' / ' + document.getElementById('hpDisk').textContent + ' / ' + document.getElementById('hpNet').textContent"), flush=True)

    # 设置页
    ev_js(window, "document.querySelector('[data-page=settings]').click()", 5)
    time.sleep(2)
    print("SETTINGS:", flush=True)
    print("  accent palette:", ev_js(window, "document.querySelectorAll('#accentPalette .swatch').length"), flush=True)
    print("  nav palette:", ev_js(window, "document.querySelectorAll('#navPalette .swatch').length"), flush=True)
    print("  accent pick:", ev_js(window, "document.getElementById('accentPick').value"), flush=True)
    print("  nav pick:", ev_js(window, "document.getElementById('navPick').value"), flush=True)

    # 修改强调色 → 验证 CSS 变量变化
    ev_js(window, "document.getElementById('accentPick').value = '#10b981'; document.getElementById('accentPick').dispatchEvent(new Event('input'))", 5)
    time.sleep(1)
    print("  accent after change:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()"), flush=True)
    print("  saved after change:", ev_js(window, "localStorage.getItem('talent_theme')"), flush=True)

    print("PROBE_SETTINGS_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
