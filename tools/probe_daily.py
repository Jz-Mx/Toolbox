# -*- coding: utf-8 -*-
"""验证：快捷入口改造（小玩意/竖排缩小/每日提问/√打卡）+ 系统信息启动时间。"""
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
    print("QUICK:", flush=True)
    print("  btns:", ev_js(window, "[...document.querySelectorAll('.quick-left .quick')].map(b => b.textContent).join(' | ')"), flush=True)
    print("  layout:", ev_js(window, "getComputedStyle(document.querySelector('.quick-left')).flexDirection + ' ' + getComputedStyle(document.querySelector('.quick-left')).width"), flush=True)
    print("DAILY:", flush=True)
    print("  q:", ev_js(window, "document.getElementById('dailyQ').textContent"), flush=True)
    print("  check exists:", ev_js(window, "!!document.getElementById('dailyCheck')"), flush=True)
    # 打卡
    ev_js(window, "document.getElementById('dailyCheck').click()", 5)
    time.sleep(0.5)
    print("  after click done:", ev_js(window, "document.getElementById('dailyCheck').classList.contains('done')"), flush=True)
    print("  saved:", ev_js(window, "localStorage.getItem(Object.keys(localStorage).find(k => k.startsWith('talent_daily_')))"), flush=True)
    # 高度对比：4 按钮总高 vs 提问框高
    print("  h compare:", ev_js(window, "(function(){var q=document.querySelector('.quick-left');var d=document.querySelector('.daily');return Math.round(d.getBoundingClientRect().height) + ' vs 4btns ' + Math.round(q.getBoundingClientRect().height);})()"), flush=True)
    print("SYSINFO:", flush=True)
    print("  row:", ev_js(window, "document.querySelectorAll('.detail-panel .d-item')[5].querySelector('b').textContent"), flush=True)
    print("PROBE_DAILY_DONE", flush=True)


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
