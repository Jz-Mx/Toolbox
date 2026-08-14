# ═══════════════════════════════════════════════════════════════
#  Talent 工具箱 · 桌面端入口
#  基于 pywebview (WebView2) + psutil，为前端提供真实系统数据
#  打包：PyInstaller 单文件模式（见 build.ps1）
# ═══════════════════════════════════════════════════════════════

import ctypes
import json
import logging
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.request
import threading
import time
import winreg
from ctypes import wintypes

import psutil

APP_NAME = "Talent 工具箱"
APP_VERSION = "1.0.0"
DEV_QQ = "3145385062"
DEV_MAIL = "talent6839@gmail.com"


# ────────────────────────────────────────────────────────────────
#  资源路径（兼容 PyInstaller 打包）
# ────────────────────────────────────────────────────────────────
def resource_path(rel=""):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel) if rel else base


def log_path():
    try:
        if hasattr(sys, "frozen"):
            return os.path.join(os.path.dirname(sys.executable), "talent.log")
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "talent.log")
    except Exception:
        return os.path.join(tempfile.gettempdir(), "talent.log")


logging.basicConfig(
    filename=log_path(),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
log = logging.getLogger("talent")


# 全局异常钩子：捕获未处理异常写入日志（便于定位打包版崩溃）
def _excepthook(exc_type, exc, tb):
    import traceback
    try:
        log.error("unhandled exception:\n%s", "".join(traceback.format_exception(exc_type, exc, tb)))
    except Exception:
        pass


sys.excepthook = _excepthook
threading.excepthook = _excepthook


# ────────────────────────────────────────────────────────────────
#  内存清理（EmptyWorkingSet）
# ────────────────────────────────────────────────────────────────
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_SET_QUOTA = 0x0100


def empty_working_sets():
    psapi = ctypes.WinDLL("psapi")
    kernel32 = ctypes.WinDLL("kernel32")

    enum_processes = psapi.EnumProcesses
    enum_processes.restype = wintypes.BOOL
    enum_processes.argtypes = [
        ctypes.POINTER(wintypes.DWORD), wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
    ]

    arr = (wintypes.DWORD * 8192)()
    needed = wintypes.DWORD()
    if not enum_processes(arr, ctypes.sizeof(arr), ctypes.byref(needed)):
        return 0

    count = needed.value // ctypes.sizeof(wintypes.DWORD)
    pids = arr[:count]

    empty_ws = psapi.EmptyWorkingSet
    empty_ws.restype = wintypes.BOOL
    empty_ws.argtypes = [wintypes.HANDLE]

    open_process = kernel32.OpenProcess
    open_process.restype = wintypes.HANDLE
    open_process.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]

    close_handle = kernel32.CloseHandle
    close_handle.restype = wintypes.BOOL
    close_handle.argtypes = [wintypes.HANDLE]

    done = 0
    for pid in pids:
        if pid == 0:
            continue
        h = open_process(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid)
        if h:
            try:
                if empty_ws(h):
                    done += 1
            finally:
                close_handle(h)
    return done


# ────────────────────────────────────────────────────────────────
#  系统信息（WMI 查询，带缓存）
# ────────────────────────────────────────────────────────────────
_sysinfo_cache = None
_sysinfo_lock = threading.Lock()


def _ps_query(script):
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True, text=True, timeout=20,
        )
        lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        return lines
    except Exception:
        return []


def _sysinfo():
    info = {}
    try:
        info["os"] = platform.platform()
        info["cpu_name"] = platform.processor() or "未知"
        info["cpu_cores"] = psutil.cpu_count(logical=False) or "?"
        info["cpu_threads"] = psutil.cpu_count(logical=True) or "?"
        info["mem_total"] = psutil.virtual_memory().total
        info["hostname"] = socket.gethostname()
        info["boot_time"] = psutil.boot_time()
        info["gpu"] = "未知"
        info["motherboard"] = "未知"
        info["bios"] = "未知"
        info["mem_spec"] = ""

        # 通过 WMI 查询显卡 / 主板 / BIOS（异步线程内执行，避免卡 UI）
        gpus = _ps_query("Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name")
        if gpus:
            info["gpu"] = " / ".join(gpus[:2])

        # 内存规格（SMBIOS 类型 + 配置频率，如 DDR4-3800）
        try:
            mt = _ps_query(
                "Get-CimInstance Win32_PhysicalMemory | Select-Object -First 1 -ExpandProperty SMBIOSMemoryType"
            )
            spd = _ps_query(
                "Get-CimInstance Win32_PhysicalMemory | Select-Object -First 1 -ExpandProperty ConfiguredClockSpeed"
            )
            mem_type = {20: "DDR", 21: "DDR2", 24: "DDR3", 26: "DDR4", 34: "DDR5"}.get(
                int(mt[0]) if mt and mt[0].isdigit() else 0, ""
            )
            freq = int(spd[0]) if spd and spd[0].isdigit() else 0
            info["mem_spec"] = (mem_type + "-" if mem_type else "") + (str(freq) + "MHz" if freq else "DDR") or "DDR"
        except Exception:
            pass

        mb = _ps_query(
            "Get-CimInstance Win32_BaseBoard | ForEach-Object { \"$($_.Manufacturer) $($_.Product)\" }"
        )
        if mb:
            info["motherboard"] = mb[0]

        bios = _ps_query("Get-CimInstance Win32_BIOS | Select-Object -ExpandProperty SMBIOSBIOSVersion")
        if bios:
            info["bios"] = bios[0]

        disks = []
        for p in psutil.disk_partitions(all=False):
            try:
                u = psutil.disk_usage(p.mountpoint)
                disks.append({"mount": p.mountpoint, "total": u.total, "used": u.used})
            except Exception:
                continue
        info["disks"] = disks
    except Exception as e:
        log.error("sysinfo error: %s", e)
    return info


# ────────────────────────────────────────────────────────────────
#  临时文件扫描 / 清理
# ────────────────────────────────────────────────────────────────
MAX_SCAN_FILES = 40000


def scan_temp_dir():
    tdir = tempfile.gettempdir()
    size = 0
    count = 0
    truncated = False
    for root, dirs, files in os.walk(tdir):
        dirs[:] = dirs[:64]
        for f in files:
            if count >= MAX_SCAN_FILES:
                truncated = True
                break
            try:
                size += os.path.getsize(os.path.join(root, f))
                count += 1
            except OSError:
                continue
        if truncated:
            break
    return {"path": tdir, "size": size, "count": count, "truncated": truncated}


def clean_temp_dir():
    tdir = tempfile.gettempdir()
    freed = 0
    removed = 0
    failed = 0

    def _onerror(err):
        nonlocal failed
        failed += 1

    for root, dirs, files in os.walk(tdir, topdown=False, onerror=_onerror):
        if removed >= MAX_SCAN_FILES:
            break
        for f in files:
            try:
                p = os.path.join(root, f)
                freed += os.path.getsize(p)
                os.remove(p)
                removed += 1
            except OSError:
                failed += 1
            if removed >= MAX_SCAN_FILES:
                break
        if removed >= MAX_SCAN_FILES:
            break
        for d in dirs:
            try:
                shutil.rmtree(os.path.join(root, d), ignore_errors=False)
                removed += 1
            except OSError:
                failed += 1
    return {"freed": freed, "removed": removed, "failed": failed}


# ────────────────────────────────────────────────────────────────
#  启动项（注册表 Run 键 + 启动文件夹）
# ────────────────────────────────────────────────────────────────
def _read_run_key(hive, path, source_name):
    items = []
    try:
        with winreg.OpenKey(hive, path) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    items.append({"name": name, "command": os.path.expandvars(str(value)), "source": source_name})
                    i += 1
                except OSError:
                    break
    except OSError:
        pass
    return items


def get_startup_items():
    items = []
    items += _read_run_key(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU\\Run")
    items += _read_run_key(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM\\Run")
    items += _read_run_key(winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run", "HKLM\\Run32")

    folders = [
        os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup"),
        os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup"),
    ]
    for folder in folders:
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                items.append({
                    "name": f,
                    "command": os.path.join(folder, f),
                    "source": "启动文件夹",
                })
    return items


# ────────────────────────────────────────────────────────────────
#  延迟测试
# ────────────────────────────────────────────────────────────────
def ping_latency():
    for host in ("223.5.5.5", "119.29.29.29", "8.8.8.8"):
        try:
            t0 = time.time()
            s = socket.create_connection((host, 53), timeout=3)
            s.close()
            return {"ms": int((time.time() - t0) * 1000), "host": host}
        except OSError:
            continue
    return {"ms": None, "host": None}


# ────────────────────────────────────────────────────────────────
#  天气查询（IP 定位 + Open-Meteo，缓存 10 分钟）
# ────────────────────────────────────────────────────────────────
_WMO_DESC = {
    0: "晴", 1: "晴间多云", 2: "多云", 3: "阴",
    45: "雾", 48: "雾凇",
    51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪", 77: "雪粒",
    80: "阵雨", 81: "阵雨", 82: "强阵雨",
    85: "阵雪", 86: "强阵雪",
    95: "雷阵雨", 96: "雷雨冰雹", 99: "强雷暴",
}

_weather_cache = None
_weather_ts = 0.0


def _ip_location():
    """IP 定位（多源容错），返回 (lat, lon, city)。"""
    sources = [
        ("http://ip-api.com/json", "ip-api"),
        ("https://ipwho.is/", "ipwho"),
    ]
    for url, kind in sources:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Talent/1.1"})
            with urllib.request.urlopen(req, timeout=6) as r:
                d = json.loads(r.read().decode("utf-8"))
            if kind == "ip-api":
                if d.get("status") != "success":
                    continue
                return d.get("lat"), d.get("lon"), d.get("city") or d.get("regionName") or "本地"
            else:
                lat, lon = d.get("latitude"), d.get("longitude")
                if lat is None or lon is None:
                    continue
                return lat, lon, d.get("city") or "本地"
        except Exception:
            continue
    return None, None, "本地"


def get_weather():
    """返回 {city, temp, desc}；失败时返回降级结果。"""
    global _weather_cache, _weather_ts
    now = time.time()
    if _weather_cache is not None and now - _weather_ts < 600:
        return _weather_cache
    try:
        # 1) IP 定位（多源容错）
        lat, lon, city = _ip_location()
        if lat is None or lon is None:
            raise ValueError("no location")
        # 2) Open-Meteo 当前天气
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,weather_code&timezone=auto"
        )
        req2 = urllib.request.Request(url, headers={"User-Agent": "Talent/1.1"})
        with urllib.request.urlopen(req2, timeout=6) as r:
            w = json.loads(r.read().decode("utf-8"))
        cur = w.get("current", {})
        temp = round(cur.get("temperature_2m", 0))
        desc = _WMO_DESC.get(cur.get("weather_code"), "未知")
        _weather_cache = {"city": city, "temp": temp, "desc": desc}
        _weather_ts = now
        return _weather_cache
    except Exception as e:
        log.warning("weather: %s", e)
        return {"city": "本地", "temp": None, "desc": "天气不可用"}


# ────────────────────────────────────────────────────────────────
#  前端桥接 API
#  注意：js_api 实例的属性会被 pywebview 6.x 递归遍历暴露，
#  因此窗口引用必须用下划线前缀（_win），避免遍历 .NET 对象链。
# ────────────────────────────────────────────────────────────────
class TalentAPI:
    def __init__(self):
        self._win = None
        self._net_last = None
        self._net_ts = None
        self._perf_lock = threading.Lock()

    # ── 窗口控制 ──
    def move_to(self, x, y):
        try:
            self._win.move(int(x), int(y))
        except Exception as e:
            log.error("move_to: %s", e)

    def minimize(self):
        try:
            self._win.minimize()
        except Exception as e:
            log.error("minimize: %s", e)

    def close(self):
        try:
            self._win.destroy()
        except Exception as e:
            log.error("close: %s", e)

    # ── 性能数据（前端每秒轮询） ──
    def get_perf(self):
        try:
            with self._perf_lock:
                vm = psutil.virtual_memory()
                cpu = psutil.cpu_percent(interval=None)
                disk = psutil.disk_usage(os.path.splitdrive(os.getcwd())[0] + "\\")
                freq_mhz = 0
                try:
                    f = psutil.cpu_freq()
                    if f:
                        freq_mhz = round(f.current or 0)
                except Exception:
                    pass

                now = time.time()
                net = psutil.net_io_counters()
                down = up = 0
                if self._net_last is not None and self._net_ts is not None:
                    dt = now - self._net_ts
                    if dt > 0:
                        down = max(0, (net.bytes_recv - self._net_last.bytes_recv) / dt)
                        up = max(0, (net.bytes_sent - self._net_last.bytes_sent) / dt)
                self._net_last = net
                self._net_ts = now

                return {
                    "cpu": round(cpu, 1),
                    "cpu_freq_mhz": freq_mhz,
                    "mem": round(vm.percent, 1),
                    "mem_total": vm.total,
                    "mem_used": vm.used,
                    "disk_pct": round(disk.percent, 1),
                    "disk_used": disk.used,
                    "disk_total": disk.total,
                    "net_down": down,
                    "net_up": up,
                    "uptime": time.time() - psutil.boot_time(),
                }
        except Exception as e:
            log.error("get_perf: %s", e)
            return {
                "cpu": 0.0, "cpu_freq_mhz": 0,
                "mem": 0.0, "disk_pct": 0.0,
                "mem_total": 0, "mem_used": 0,
                "disk_used": 0, "disk_total": 0,
                "net_down": 0.0, "net_up": 0.0, "uptime": 0.0,
            }

    # ── 系统信息（带缓存） ──
    def get_sysinfo(self):
        global _sysinfo_cache
        if _sysinfo_cache is None:
            with _sysinfo_lock:
                if _sysinfo_cache is None:
                    _sysinfo_cache = _sysinfo()
        return _sysinfo_cache

    # ── 内存清理 ──
    def clean_memory(self):
        before = psutil.virtual_memory().percent
        done = empty_working_sets()
        time.sleep(0.6)
        after = psutil.virtual_memory().percent
        log.info("memory clean: %d processes, %.1f%% -> %.1f%%", done, before, after)
        return {"before": round(before, 1), "after": round(after, 1), "freed": round(before - after, 1), "processes": done}

    # ── 临时文件 ──
    def scan_temp(self):
        return scan_temp_dir()

    def clean_temp(self):
        r = clean_temp_dir()
        log.info("temp clean: freed=%d removed=%d failed=%d", r["freed"], r["removed"], r["failed"])
        return r

    # ── 进程管理 ──
    def get_top_processes(self, n=10):
        # 预热 cpu_percent
        for p in psutil.process_iter(["pid"]):
            try:
                p.cpu_percent(None)
            except Exception:
                pass
        time.sleep(0.25)
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                info = p.info
                mem = (info["memory_info"].rss or 0) / (1024 ** 2)
                procs.append((mem, info["pid"], info["name"] or "?", info["cpu_percent"] or 0))
            except Exception:
                continue
        procs.sort(reverse=True)
        return [
            {"pid": pid, "name": name, "cpu": round(cpu, 1), "mem_mb": round(mem, 0)}
            for mem, pid, name, cpu in procs[:n]
        ]

    def kill_process(self, pid):
        name = "未知"
        try:
            pid = int(pid)
            if pid == os.getpid():
                return {"ok": False, "name": "Talent.exe", "msg": "不能结束自己"}
            p = psutil.Process(pid)
            name = p.name() or str(pid)
            p.terminate()
            p.wait(timeout=3)
            return {"ok": True, "name": name}
        except psutil.NoSuchProcess:
            return {"ok": True, "name": name}
        except psutil.AccessDenied:
            return {"ok": False, "name": name, "msg": "权限不足"}
        except Exception as e:
            log.error("kill %s: %s", pid, e)
            return {"ok": False, "name": name, "msg": str(e)}

    # ── 启动项 ──
    def get_startup_items(self):
        return get_startup_items()

    # ── 网络延迟 ──
    def ping(self):
        return ping_latency()

    # ── 天气 ──
    def get_weather(self):
        return get_weather()

    # ── 前端日志上报 ──
    def log(self, level, msg):
        getattr(log, level if level in ("info", "warning", "error") else "info")("js: %s", msg)


# ────────────────────────────────────────────────────────────────
#  入口
# ────────────────────────────────────────────────────────────────
def main():
    try:
        import webview
    except ImportError:
        log.error("pywebview 未安装：pip install pywebview")
        sys.exit(1)

    api = TalentAPI()
    index = os.path.join(resource_path("web"), "index.html")
    log.info("start %s v%s, web=%s", APP_NAME, APP_VERSION, index)

    window = webview.create_window(
        APP_NAME,
        index,
        js_api=api,
        width=1180,
        height=760,
        min_size=(960, 620),
        frameless=True,
        background_color="#171030",
    )
    api._win = window
    webview.start()


if __name__ == "__main__":
    main()
