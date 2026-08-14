# -*- coding: utf-8 -*-
"""验证：CPU/内存双线同图（同基准）。"""
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
    ev_js(window, "document.querySelector('[data-page=monitor]').click()", 5)
    time.sleep(4)
    print("CHART:", flush=True)
    print("  cm canvas:", ev_js(window, "!!document.getElementById('chartCm')"), flush=True)
    print("  old canvases gone:", ev_js(window, "!document.getElementById('chartCpu') && !document.getElementById('chartMem')"), flush=True)
    print("  cmNow:", ev_js(window, "document.getElementById('cmNow').textContent"), flush=True)
    print("  cm size:", ev_js(window, "document.getElementById('chartCm').clientWidth + 'x' + document.getElementById('chartCm').clientHeight"), flush=True)
    print("  net size:", ev_js(window, "document.getElementById('chartNet').clientWidth + 'x' + document.getElementById('chartNet').clientHeight"), flush=True)
    # 绘制验证：canvas 非空白（有像素变化）
    print("  cm pixels:", ev_js(window, "(function(){var c=document.getElementById('chartCm');var d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;var n=0;for(var i=3;i<d.length;i+=16){if(d[i]>0)n++;}return n;})()"), flush=True)
    print("PROBE_CM_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
