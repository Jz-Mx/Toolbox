# -*- coding: utf-8 -*-
"""用 Pillow 生成标准多尺寸 ICO（16/24/32/48/64/128/256），供 exe 与快捷方式使用。

图标设计：紫粉渐变圆底 + 白色感叹星 + 猫耳 + 高光（二次元风，简洁）。
"""
import math
import os
import struct

from PIL import Image, ImageDraw

SIZE = 256


def lerp(a, b, t):
    return int(a + (b - a) * t)


def in_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def build(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    s = size / 256.0

    def P(v):
        return int(v * s)

    purple = (139, 92, 246)
    pink = (236, 72, 153)

    for y in range(size):
        for x in range(size):
            r = g = b = a = 0
            # 猫耳（两个圆）
            if in_ellipse(x, y, P(64), P(56), P(46), P(44)) and (x + y) < P(122):
                r, g, b, a = 244, 170, 200, 255
            elif in_ellipse(x, y, P(192), P(56), P(46), P(44)) and (y - x) < P(-78):
                r, g, b, a = 244, 170, 200, 255
            # 主圆底（紫粉渐变）
            if in_ellipse(x, y, P(128), P(150), P(110), P(106)):
                t = max(0.0, min(1.0, (x + y - P(30)) / P(380)))
                r = lerp(purple[0], pink[0], t)
                g = lerp(purple[1], pink[1], t)
                b = lerp(purple[2], pink[2], t)
                a = 255
                # 高光
                if in_ellipse(x, y, P(96), P(108), P(42), P(28)):
                    r = lerp(r, 255, 0.32)
                    g = lerp(g, 255, 0.32)
                    b = lerp(b, 255, 0.32)
            # 白色感叹星（圆点 + 底部小点）
            dx, dy = x - P(128), y - P(138)
            dist = math.hypot(dx, dy)
            if dist < P(30) and dist > P(6):
                r, g, b, a = 255, 255, 255, 255
            px[x, y] = (r, g, b, a)

    return img


out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "talent.ico")
os.makedirs(os.path.dirname(out), exist_ok=True)

sizes = [16, 24, 32, 48, 64, 128, 256]
images = {s: build(s) for s in sizes}

# 手动构造全 BMP 帧 ICO（最兼容：Windows 各版本资源管理器均正常显示）
frames = []
header = struct.pack("<HHH", 0, 1, len(sizes))
offset = 6 + 16 * len(sizes)
for s in sizes:
    img = images[s]
    w = h = s
    px = img.load()
    bmp_header = struct.pack("<IiiHHIIIIII", 40, w, h * 2, 1, 32, 0, w * h * 4, 0, 0, 0, 0)
    pixel = bytearray()
    for y in range(h - 1, -1, -1):  # 自下而上
        for x in range(w):
            r, g, b, a = px[x, y]
            pixel += bytes((b, g, r, a))
    mask_row = ((w + 31) // 32) * 4
    mask = bytes(mask_row * h)
    frame = bmp_header + bytes(pixel) + mask
    header += struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, 1, 32, len(frame), offset)
    frames.append(frame)
    offset += len(frame)

with open(out, "wb") as f:
    f.write(header + b"".join(frames))
print("icon written (BMP frames):", os.path.abspath(out), os.path.getsize(out), "bytes, sizes:", sizes)
