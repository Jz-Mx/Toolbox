# -*- coding: utf-8 -*-
"""验证：CPU/内存两独立图，曲线高度一致（动态 Y 轴）。"""
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
    time.sleep(5)
    print("CHARTS:", flush=True)
    print("  two charts:", ev_js(window, "!!document.getElementById('chartCpu') && !!document.getElementById('chartMem')"), flush=True)
    print("  merged gone:", ev_js(window, "!document.getElementById('chartCm')"), flush=True)
    print("  now:", ev_js(window, "document.getElementById('cpuNow').textContent + ' / ' + document.getElementById('memNow').textContent"), flush=True)
    # 曲线高度：采样两图曲线像素的垂直跨度（非空白像素 min/max y）
    expr = "(function(){function span(c){var cv=document.getElementById(c);var d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;var minY=9999,maxY=-1;for(var y=0;y<cv.height;y++){for(var x=0;x<cv.width;x+=4){var i=(y*cv.width+x)*4;if(d[i+3]>0){if(y<minY)minY=y;if(y>maxY)maxY=y;}}}return minY===9999?0:maxY-minY;}return 'cpu='+span('chartCpu')+' mem='+span('chartMem');})()"
    print("  spans:", ev_js(window, expr, 15), flush=True)
    print("PROBE_H_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#14101f",
)
api._win = window
webview.start(probe, window)
