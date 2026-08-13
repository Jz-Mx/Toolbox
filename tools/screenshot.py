# -*- coding: utf-8 -*-
"""截图 v3：EnumWindows 按标题查找 Talent 窗口并截图分析（不依赖 PowerShell 子进程）。"""
import ctypes
import ctypes.wintypes
import os
import struct
import subprocess
import zlib

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# ── 按窗口标题查找（EnumWindows，取可见窗口） ──
found = []


@ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
def _enum_cb(hwnd, lparam):
    if not user32.IsWindowVisible(hwnd):
        return True
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if "Talent" in buf.value:
            r = ctypes.wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            found.append((hwnd, (r.right - r.left) * (r.bottom - r.top)))
    return True


user32.EnumWindows(_enum_cb, 0)
if not found:
    print("WINDOW_NOT_FOUND")
    raise SystemExit(1)
found.sort(key=lambda t: t[1], reverse=True)
hwnd = found[0][0]
print("hwnd:", hwnd)

# 将窗口置前，确保 BitBlt 不被遮挡
user32.SetForegroundWindow(hwnd)
import time
time.sleep(1.5)

rect = ctypes.wintypes.RECT()
user32.GetWindowRect(hwnd, ctypes.byref(rect))
ww, wh = rect.right - rect.left, rect.bottom - rect.top
print(f"window rect: {rect.left},{rect.top} {ww}x{wh}")

hdc_win = user32.GetWindowDC(hwnd)
hdc_mem = gdi32.CreateCompatibleDC(hdc_win)
bmp = gdi32.CreateCompatibleBitmap(hdc_win, ww, wh)
gdi32.SelectObject(hdc_mem, bmp)

# PrintWindow 对 WebView2 可能挂起，改用 BitBlt 屏幕拷贝窗口区域
screen_dc = user32.GetDC(0)
try:
    gdi32.BitBlt(hdc_mem, 0, 0, ww, wh, screen_dc, rect.left, rect.top, 0x00CC0020)
finally:
    user32.ReleaseDC(0, screen_dc)

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.wintypes.DWORD),
        ("biWidth", ctypes.wintypes.LONG),
        ("biHeight", ctypes.wintypes.LONG),
        ("biPlanes", ctypes.wintypes.WORD),
        ("biBitCount", ctypes.wintypes.WORD),
        ("biCompression", ctypes.wintypes.DWORD),
        ("biSizeImage", ctypes.wintypes.DWORD),
        ("biXPelsPerMeter", ctypes.wintypes.LONG),
        ("biYPelsPerMeter", ctypes.wintypes.LONG),
        ("biClrUsed", ctypes.wintypes.DWORD),
        ("biClrImportant", ctypes.wintypes.DWORD),
    ]

bih = BITMAPINFOHEADER()
bih.biSize = ctypes.sizeof(BITMAPINFOHEADER)
bih.biWidth = ww
bih.biHeight = -wh
bih.biPlanes = 1
bih.biBitCount = 32
bih.biCompression = 0

buf = ctypes.create_string_buffer(ww * wh * 4)
gdi32.GetDIBits(hdc_mem, bmp, 0, wh, buf, ctypes.byref(bih), 0)
data = memoryview(buf).cast("B")

n = 0
dark = light = purple = pink = cyan = 0
for y in range(0, wh, 8):
    for x in range(0, ww, 8):
        i = (y * ww + x) * 4
        b, g, r = data[i], data[i + 1], data[i + 2]
        n += 1
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if lum < 60:
            dark += 1
        elif lum > 170:
            light += 1
        if r > 110 and b > 130 and g < 120:
            purple += 1
        if r > 170 and b > 120 and g < 130:
            pink += 1
        if g > 150 and b > 160 and r < 120:
            cyan += 1

print(f"samples={n} dark={dark} light={light} purple={purple} pink={pink} cyan={cyan}")
print("VERDICT:", "RENDERED" if (light > n * 0.02 and purple > n * 0.01) else "UNKNOWN")


def save_png(path, ww, wh, data):
    raw = b""
    for y in range(wh):
        raw += b"\x00"
        for x in range(ww):
            i = (y * ww + x) * 4
            raw += bytes((data[i + 2], data[i + 1], data[i]))

    def chunk(tag, payload):
        c = tag + payload
        return struct.pack(">I", len(payload)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", ww, wh, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shot.png")
print("skip png save (slow)")
