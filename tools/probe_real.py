# -*- coding: utf-8 -*-
"""验证：曲线真实高度（排除网格线，alpha>60 的曲线像素）。"""
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
    ev_js(window, "document.querySelector('[data-page=monitor]').click()", 5)
    time.sleep(5)
    print("CHART:", flush=True)
    print("  cpuNow:", ev_js(window, "document.getElementById('cpuNow').textContent"), flush=True)
    print("  memNow:", ev_js(window, "document.getElementById('memNow').textContent"), flush=True)
    expr = "(function(){function top(c){var cv=document.getElementById(c);var d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;var minY=9999;for(var y=0;y<cv.height;y++){for(var x=0;x<cv.width;x+=2){var i=(y*cv.width+x)*4;if(d[i+3]>60){if(y<minY)minY=y;break;}}if(minY<9999)break;}return minY===9999?-1:minY;}return 'cpuTop='+top('chartCpu')+' memTop='+top('chartMem');})()"
    print("  ", ev_js(window, expr, 15), flush=True)
    print("  (画布高 150：CPU 低使用率应贴近底部 ~125px，内存 30-60% 应在 ~60-100px)", flush=True)
    print("PROBE_REAL2_DONE", flush=True)


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
