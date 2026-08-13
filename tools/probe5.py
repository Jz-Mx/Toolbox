# -*- coding: utf-8 -*-
"""综合验证 v6：桥接修复后验证真实数据渲染 + 计算器/番茄钟交互。"""
import json
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
    time.sleep(7)

    print("BRIDGE:", flush=True)
    print("  hasNative:", ev_js(window, "API.hasNative"), flush=True)

    # 首页（桥接就绪后应显示真实数据）
    print("DASH:", flush=True)
    print("  cpu%:", ev_js(window, "document.getElementById('cpuNum').textContent"), flush=True)
    print("  mem%:", ev_js(window, "document.getElementById('memNum').textContent"), flush=True)
    print("  disk%:", ev_js(window, "document.getElementById('diskPct').textContent"), flush=True)
    print("  netDown:", ev_js(window, "document.getElementById('netDown').textContent"), flush=True)
    print("  ping:", ev_js(window, "document.getElementById('netPing').textContent"), flush=True)

    # 监控页（真实系统信息）
    ev_js(window, "document.querySelector('[data-page=monitor]').click()", 5)
    time.sleep(4)
    print("MONITOR:", flush=True)
    print("  os:", ev_js(window, "document.querySelector('#sysinfoBody tr td:last-child').textContent"), flush=True)
    print("  cpu row:", ev_js(window, "document.querySelectorAll('#sysinfoBody tr')[1].querySelector('td:last-child').textContent"), flush=True)
    print("  gpu row:", ev_js(window, "document.querySelectorAll('#sysinfoBody tr')[4].querySelector('td:last-child').textContent"), flush=True)
    print("  mb row:", ev_js(window, "document.querySelectorAll('#sysinfoBody tr')[5].querySelector('td:last-child').textContent"), flush=True)
    print("  disks:", ev_js(window, "document.querySelectorAll('.disk-item').length"), flush=True)
    print("  disk0:", ev_js(window, "document.querySelector('.disk-item .disk-top').textContent"), flush=True)

    # 工具页（真实进程/启动项）
    ev_js(window, "document.querySelector('[data-page=tools]').click()", 5)
    time.sleep(4)
    print("TOOLS:", flush=True)
    print("  procs:", ev_js(window, "[...document.querySelectorAll('#procList .proc-item')].map(p => p.textContent.trim().replace(/\\s+/g,' ')).join(' | ')"), flush=True)
    ev_js(window, "document.getElementById('btnRefreshStartup').click()", 5)
    time.sleep(3)
    print("  startup:", ev_js(window, "[...document.querySelectorAll('#startupList .proc-item')].map(p => p.textContent.trim().replace(/\\s+/g,' ')).join(' | ')"), flush=True)

    # 小玩意页（计算器 / 番茄钟真实交互）
    ev_js(window, "document.querySelector('[data-page=apps]').click()", 5)
    time.sleep(2)
    print("APPS:", flush=True)
    ev_js(window, "document.querySelector('#calcGrid [data-k=\"7\"]').click()", 5)
    time.sleep(0.4)
    print("  calc after 7:", ev_js(window, "document.getElementById('calcScreen').textContent"), flush=True)
    ev_js(window, "document.querySelector('#calcGrid [data-k=\"+\"]').click(); document.querySelector('#calcGrid [data-k=\"8\"]').click(); document.querySelector('#calcGrid [data-k=\"=\"]').click()", 5)
    time.sleep(0.4)
    print("  calc 7+8=:", ev_js(window, "document.getElementById('calcScreen').textContent"), flush=True)
    ev_js(window, "document.querySelector('#calcGrid [data-k=\"C\"]').click()", 5)
    time.sleep(0.3)
    print("  calc cleared:", ev_js(window, "document.getElementById('calcScreen').textContent"), flush=True)

    ev_js(window, "document.querySelector('.pomo-modes [data-min=\"5\"]').click()", 5)
    time.sleep(0.4)
    print("  pomo mode5:", ev_js(window, "document.getElementById('pomoTime').textContent"), flush=True)
    ev_js(window, "document.getElementById('pomoStart').click()", 5)
    time.sleep(2.5)
    print("  pomo running:", ev_js(window, "document.getElementById('pomoTime').textContent + ' | ' + document.getElementById('pomoState').textContent"), flush=True)

    print("PROBE6_DONE", flush=True)


index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "index.html")
api = TalentAPI()
window = webview.create_window(
    "probe", index, js_api=api,
    width=1180, height=760, min_size=(960, 620),
    frameless=True, background_color="#171030",
)
api._win = window
webview.start(probe, window)
