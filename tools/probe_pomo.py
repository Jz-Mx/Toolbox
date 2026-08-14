# -*- coding: utf-8 -*-
"""验证：番茄钟滚轮调时（滚轮分/中键秒）+ 页面切换。"""
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
    # 页面切换
    ev_js(window, "document.querySelector('[data-page=apps]').click()", 5)
    time.sleep(2)
    print("APPS:", flush=True)
    print("  wheel exists:", ev_js(window, "!!document.getElementById('pomoWheel')"), flush=True)
    print("  time t0:", ev_js(window, "document.getElementById('pomoTime').textContent"), flush=True)
    # 滚轮上滚（+1 分钟）
    ev_js(window, "(function(){var w=document.getElementById('pomoWheel');w.dispatchEvent(new WheelEvent('wheel',{deltaY:-100,bubbles:true,cancelable:true}));})()", 5)
    time.sleep(0.5)
    print("  after wheel up:", ev_js(window, "document.getElementById('pomoTime').textContent"), flush=True)
    # 滚轮下滚（-1 分钟）
    ev_js(window, "(function(){var w=document.getElementById('pomoWheel');w.dispatchEvent(new WheelEvent('wheel',{deltaY:100,bubbles:true,cancelable:true}));})()", 5)
    time.sleep(0.5)
    print("  after wheel down:", ev_js(window, "document.getElementById('pomoTime').textContent"), flush=True)
    # 中键按下 + 上滚（+5 秒）
    ev_js(window, "(function(){var w=document.getElementById('pomoWheel');w.dispatchEvent(new MouseEvent('mousedown',{button:1,bubbles:true,cancelable:true}));w.dispatchEvent(new WheelEvent('wheel',{deltaY:-100,bubbles:true,cancelable:true}));window.dispatchEvent(new MouseEvent('mouseup',{button:1,bubbles:true}));})()", 5)
    time.sleep(0.5)
    print("  after mid+wheel up:", ev_js(window, "document.getElementById('pomoTime').textContent"), flush=True)
    # 中键 + 下滚（-5 秒）
    ev_js(window, "(function(){var w=document.getElementById('pomoWheel');w.dispatchEvent(new MouseEvent('mousedown',{button:1,bubbles:true,cancelable:true}));w.dispatchEvent(new WheelEvent('wheel',{deltaY:100,bubbles:true,cancelable:true}));window.dispatchEvent(new MouseEvent('mouseup',{button:1,bubbles:true}));})()", 5)
    time.sleep(0.5)
    print("  after mid+wheel down:", ev_js(window, "document.getElementById('pomoTime').textContent"), flush=True)
    print("PROBE_POMO_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
