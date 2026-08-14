# -*- coding: utf-8 -*-
"""验证：每日提问升级（输入框/发送/星星/答案校验/双击重置/高度）。"""
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
    time.sleep(10)
    print("DAILY:", flush=True)
    print("  q:", ev_js(window, "document.getElementById('dailyQ').textContent"), flush=True)
    print("  input:", ev_js(window, "!!document.getElementById('dailyInput') && !!document.getElementById('dailySend')"), flush=True)
    print("  star:", ev_js(window, "document.getElementById('dailyCheck').textContent"), flush=True)
    # 高度：5 按钮 vs 提问框
    print("  h:", ev_js(window, "(function(){var q=document.querySelector('.quick-left');var d=document.querySelector('.daily');return Math.round(d.getBoundingClientRect().height) + ' vs ' + Math.round(q.getBoundingClientRect().height);})()"), flush=True)
    # 错误答案
    ev_js(window, "document.getElementById('dailyInput').value='999'; document.getElementById('dailySend').click()", 5)
    time.sleep(0.6)
    print("  wrong ans done:", ev_js(window, "document.getElementById('dailyCheck').classList.contains('done')"), flush=True)
    # 正确答案（读取题目答案库：直接调用前端模块不易，用 localStorage 状态取 idx）
    ev_js(window, "document.getElementById('dailyInput').value = '999'; document.getElementById('dailyInput').value = String((function(){var s=JSON.parse(localStorage.getItem('talent_daily'));return s.idx;})()); document.getElementById('dailySend').click()", 5)
    time.sleep(0.6)
    print("  state:", ev_js(window, "localStorage.getItem('talent_daily')"), flush=True)
    print("  star done after:", ev_js(window, "document.getElementById('dailyCheck').classList.contains('done')"), flush=True)
    print("  star anim:", ev_js(window, "getComputedStyle(document.getElementById('dailyCheck')).animationName"), flush=True)
    # 双击重置
    ev_js(window, "document.getElementById('dailyCheck').dispatchEvent(new MouseEvent('dblclick',{bubbles:true}))", 5)
    time.sleep(0.6)
    print("  after dblclick done:", ev_js(window, "document.getElementById('dailyCheck').classList.contains('done')"), flush=True)
    print("  state2:", ev_js(window, "localStorage.getItem('talent_daily')"), flush=True)
    print("PROBE_DAILY2_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
app.start_max_freq_detect()
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
