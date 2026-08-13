# -*- coding: utf-8 -*-
"""生成 Talent 应用图标（纯标准库，PNG 内嵌 ICO 格式）。"""

import os
import struct
import zlib

SIZE = 256


def build_png(width, height, pixel_fn):
    """pixel_fn(x, y) -> (r, g, b, a)，输出 RGBA PNG 字节。"""
    raw = b""
    for y in range(height):
        raw += b"\x00"  # filter: None
        for x in range(width):
            r, g, b, a = pixel_fn(x, y)
            raw += bytes((int(r), int(g), int(b), int(a)))

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def in_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def lerp(a, b, t):
    return a + (b - a) * t


def main():
    purple = (139, 92, 246)
    pink = (236, 72, 153)
    star_col = (255, 255, 255)
    ear_col = (244, 170, 200)

    def pixel(x, y):
        # 背景透明
        a = 0.0
        r = g = b = 0

        # 猫耳（两个圆角三角近似：用椭圆+三角形组合简化——直接画两个圆）
        if in_ellipse(x, y, 62, 52, 44, 40) and (x + y) < 118:
            r, g, b, a = *ear_col, 1.0
        elif in_ellipse(x, y, 194, 52, 44, 40) and (y - x) < -76 + 256:
            r, g, b, a = *ear_col, 1.0

        # 主圆底（紫粉渐变）
        if in_ellipse(x, y, 128, 150, 108, 104):
            t = (x + y - 30) / 380
            t = max(0.0, min(1.0, t))
            r = lerp(purple[0], pink[0], t)
            g = lerp(purple[1], pink[1], t)
            b = lerp(purple[2], pink[2], t)
            a = 1.0
            # 高光
            if in_ellipse(x, y, 96, 108, 40, 26):
                r, g, b = lerp(r, 255, 0.35), lerp(g, 255, 0.35), lerp(b, 255, 0.35)

        # 白色五角星
        dx, dy = x - 128, y - 138
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 30:
            ang = (abs(dx) / (dist + 1e-9))
            # 简化：菱形星
            if abs(dx) * 0.62 + abs(dy) * 0.62 < 30 and dist > 6:
                r, g, b, a = *star_col, 1.0

        return r, g, b, a * 255

    png = build_png(SIZE, SIZE, pixel)

    # ICO 封装（256x256 使用 PNG 内嵌）
    ico = struct.pack("<HHH", 0, 1, 1)
    ico += struct.pack("<BBBBHHII", 0, 0, 0, 0, 1, 32, len(png), 22)
    ico += png

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "talent.ico")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(ico)
    print("icon written:", os.path.abspath(out), len(ico), "bytes")


if __name__ == "__main__":
    main()
