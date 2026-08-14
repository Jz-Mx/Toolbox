# -*- coding: utf-8 -*-
"""验证外观设置扩展：玻璃风格切换、模糊度滑块、关于页新内容。"""
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
    ev_js(window, "document.querySelector('[data-page=about]').click()", 5)
    time.sleep(2)
    print("APPEARANCE:", flush=True)
    print("  modes:", ev_js(window, "[...document.querySelectorAll('#glassModes .mode')].map(m => m.textContent + (m.classList.contains('active') ? '*' : '')).join(' ')"), flush=True)
    print("  blur range:", ev_js(window, "document.getElementById('glassBlur').value + 'px / ' + document.getElementById('glassBlurVal').textContent"), flush=True)
    print("  accent:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()"), flush=True)

    # 切换水玻璃
    ev_js(window, "document.querySelector('#glassModes [data-mode=water]').click()", 5)
    time.sleep(1)
    print("  water mode blur:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--glass-blur').trim()"), flush=True)
    print("  water mode bg:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--glass-bg').trim()"), flush=True)
    print("  water mode sat:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--glass-sat').trim()"), flush=True)

    # 调整模糊度
    ev_js(window, "document.getElementById('glassBlur').value = '50'; document.getElementById('glassBlur').dispatchEvent(new Event('input'))", 5)
    time.sleep(0.8)
    print("  blur 50px:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--glass-blur').trim()"), flush=True)
    print("  saved:", ev_js(window, "localStorage.getItem('talent_theme')"), flush=True)

    # 恢复默认
    ev_js(window, "document.getElementById('btnAppearanceReset').click()", 5)
    time.sleep(1)
    print("  after reset:", ev_js(window, "getComputedStyle(document.documentElement).getPropertyValue('--glass-blur').trim() + ' / mode=' + document.querySelector('#glassModes .mode.active').dataset.mode"), flush=True)

    # 关于页内容
    print("ABOUT EXTRA:", flush=True)
    print("  rows:", ev_js(window, "[...document.querySelectorAll('.about-extra .ae-row')].map(r => r.textContent.trim().replace(/\\s+/g,' ')).join(' | ')"), flush=True)
    print("  version:", ev_js(window, "document.querySelector('.about-ver').textContent"), flush=True)

    print("PROBE_APPEARANCE_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
