# -*- coding: utf-8 -*-
"""诊断：模拟资源管理器提取 exe 图标（SHGetFileInfo），检查 ICO 帧结构。"""
import ctypes
import struct

exe = r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent\dist\Talent.exe"
ico = r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent\assets\talent.ico"


class SHFILEINFO(ctypes.Structure):
    _fields_ = [
        ("hIcon", ctypes.c_void_p),
        ("iIcon", ctypes.c_int),
        ("dwAttributes", ctypes.c_ulong),
        ("szDisplayName", ctypes.c_wchar * 260),
        ("szTypeName", ctypes.c_wchar * 80),
    ]


shell32 = ctypes.WinDLL("shell32")
SHGFI_ICON = 0x100
SHGFI_LARGEICON = 0x0
SHGFI_SMALLICON = 0x1
user32 = ctypes.WinDLL("user32")

for name, flags in [("大图标", SHGFI_ICON | SHGFI_LARGEICON), ("小图标", SHGFI_ICON | SHGFI_SMALLICON)]:
    sfi = SHFILEINFO()
    r = shell32.SHGetFileInfoW(exe, 0, ctypes.byref(sfi), ctypes.sizeof(sfi), flags)
    if r and sfi.hIcon:
        print(f"SHGetFileInfo {name}: OK hIcon={sfi.hIcon:#x}")
        user32.DestroyIcon(ctypes.c_void_p(sfi.hIcon))
    else:
        print(f"SHGetFileInfo {name}: FAIL r={r} hIcon={sfi.hIcon:#x}")

print("--- talent.ico 帧结构 ---")
with open(ico, "rb") as f:
    data = f.read()
reserved, itype, count = struct.unpack("<HHH", data[:6])
print(f"reserved={reserved} type={itype} count={count}")
for i in range(count):
    w, h, colors, res, planes, bpp, size, offset = struct.unpack("<BBBBHHII", data[6 + 16 * i: 6 + 16 * (i + 1)])
    frame = data[offset:offset + size]
    is_png = frame[:8] == b"\x89PNG\r\n\x1a\n"
    print(f"  帧{i}: {w or 256}x{h or 256} bpp={bpp} size={size} 格式={'PNG' if is_png else 'BMP'}")
