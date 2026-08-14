# -*- coding: utf-8 -*-
"""验证：番茄钟左键拖拽逐秒调节 + 下限 5 秒（可拖到 1 分钟以内）。"""
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
    ev_js(window, "document.querySelector('[data-page=apps]').click()", 5)
    time.sleep(4)
    # 1) 向下拖 30px → 应 -30 秒（逐秒）：25:00 -> 24:30
    t1 = ev_js(window, """(function(){
      const w = document.getElementById('pomoWheel');
      w.dispatchEvent(new MouseEvent('mousedown',{button:0,screenY:500,bubbles:true}));
      window.dispatchEvent(new MouseEvent('mousemove',{screenY:530,bubbles:true}));
      const t = document.getElementById('pomoTime').textContent;
      window.dispatchEvent(new MouseEvent('mouseup',{button:0,bubbles:true}));
      return t;
    })()""", 15)
    print("向下拖 30px:", t1, flush=True)
    # 2) 大幅向下拖 → 应卡在下限 00:05（修复：可到 1 分钟以内）
    t2 = ev_js(window, """(function(){
      const w = document.getElementById('pomoWheel');
      w.dispatchEvent(new MouseEvent('mousedown',{button:0,screenY:500,bubbles:true}));
      window.dispatchEvent(new MouseEvent('mousemove',{screenY:5000,bubbles:true}));
      const t = document.getElementById('pomoTime').textContent;
      window.dispatchEvent(new MouseEvent('mouseup',{button:0,bubbles:true}));
      return t;
    })()""", 15)
    print("大幅向下拖:", t2, flush=True)
    # 3) 向上拖 10px → 应 +10 秒：00:05 -> 00:15
    t3 = ev_js(window, """(function(){
      const w = document.getElementById('pomoWheel');
      w.dispatchEvent(new MouseEvent('mousedown',{button:0,screenY:500,bubbles:true}));
      window.dispatchEvent(new MouseEvent('mousemove',{screenY:490,bubbles:true}));
      const t = document.getElementById('pomoTime').textContent;
      window.dispatchEvent(new MouseEvent('mouseup',{button:0,bubbles:true}));
      return t;
    })()""", 15)
    print("向上拖 10px:", t3, flush=True)
    # 4) 滚轮减分钟 → 25 分钟减到 5 秒下限附近：先加回 25 分钟再滚轮向下一次（-1 分钟）
    t4 = ev_js(window, """(function(){
      const w = document.getElementById('pomoWheel');
      w.dispatchEvent(new WheelEvent('wheel',{deltaY:100,bubbles:true,cancelable:true}));
      const t = document.getElementById('pomoTime').textContent;
      return t;
    })()""", 15)
    print("滚轮向下一次:", t4, flush=True)
    print("PROBE_POMO_DONE", flush=True)


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
