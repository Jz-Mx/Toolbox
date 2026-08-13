# -*- coding: utf-8 -*-
"""Talent 后端核心 API 单元测试（Windows 真实环境）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import app


@pytest.fixture(scope="module")
def api():
    return app.TalentAPI()


def test_get_perf_shape(api):
    p = api.get_perf()
    for k in ("cpu", "mem", "disk_pct", "disk_used", "disk_total", "net_down", "net_up", "uptime"):
        assert k in p, f"缺少字段 {k}"
    assert 0 <= p["cpu"] <= 100
    assert 0 <= p["mem"] <= 100
    assert p["disk_total"] > 0
    assert p["uptime"] > 0


def test_sysinfo_shape(api):
    s = api.get_sysinfo()
    for k in ("os", "cpu_name", "cpu_cores", "cpu_threads", "mem_total",
              "gpu", "motherboard", "bios", "hostname", "boot_time", "disks"):
        assert k in s, f"缺少字段 {k}"
    assert s["mem_total"] > 0
    assert isinstance(s["disks"], list)
    assert len(s["disks"]) >= 1
    d = s["disks"][0]
    assert d["total"] > 0 and d["used"] > 0


def test_scan_temp_shape(api):
    r = api.scan_temp()
    assert "path" in r and "size" in r and "count" in r
    assert r["size"] >= 0
    assert r["count"] >= 0
    assert os.path.isdir(r["path"])


def test_top_processes_shape(api):
    procs = api.get_top_processes(5)
    assert isinstance(procs, list)
    assert 0 < len(procs) <= 5
    for p in procs:
        assert p["pid"] > 0
        assert p["name"]
        assert p["mem_mb"] >= 0


def test_startup_items_shape(api):
    items = api.get_startup_items()
    assert isinstance(items, list)
    for it in items:
        assert it["name"]
        assert it["source"]
        assert "command" in it


def test_ping_shape(api):
    r = api.ping()
    assert "ms" in r and "host" in r
    if r["ms"] is not None:
        assert r["ms"] >= 0


def test_empty_working_sets_returns_int():
    n = app.empty_working_sets()
    assert isinstance(n, int)
    assert n >= 0


def test_kill_missing_process(api):
    r = api.kill_process(99999999)
    assert r["ok"] is True  # 不存在的进程视为已结束


def test_kill_self_protected(api):
    import os
    r = api.kill_process(os.getpid())
    assert r["ok"] is False
    assert "自己" in r.get("msg", "")


def test_move_minimize_no_crash(api):
    # 无窗口时调用不应抛异常
    api.move_to(100, 100)
    api.minimize()
    api.close()
