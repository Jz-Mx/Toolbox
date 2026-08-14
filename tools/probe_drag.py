# -*- coding: utf-8 -*-
"""验证：拖拽仅 dragArea 触发，内容区/标题栏其他不触发。"""
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
    # 安装计数器 + 测试
    r = ev_js(window, """
      (function(){
        window.__moves = 0;
        const orig = window.pywebview.api.move_to.bind(window.pywebview.api);
        window.pywebview.api.move_to = function(...a){ window.__moves++; return orig(...a); };
        // 1) 内容区（hero）mousedown + mousemove → 不应触发
        document.querySelector('.hero').dispatchEvent(new MouseEvent('mousedown',{button:0,bubbles:true}));
        window.dispatchEvent(new MouseEvent('mousemove',{screenX:200,screenY:200,bubbles:true}));
        const afterContent = window.__moves;
        window.dispatchEvent(new MouseEvent('mouseup',{button:0,bubbles:true}));
        // 2) dragArea mousedown + mousemove → 应触发
        document.getElementById('dragArea').dispatchEvent(new MouseEvent('mousedown',{button:0,bubbles:true}));
        window.dispatchEvent(new MouseEvent('mousemove',{screenX:150,screenY:150,bubbles:true}));
        const afterDrag = window.__moves;
        window.dispatchEvent(new MouseEvent('mouseup',{button:0,bubbles:true}));
        return 'contentMoves=' + afterContent + ' dragMoves=' + (afterDrag - afterContent);
      })()
    """, 15)
    print("RESULT:", r, flush=True)
    print("（期望 contentMoves=0 dragMoves>=1）", flush=True)
    print("PROBE_DRAG_DONE", flush=True)


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
