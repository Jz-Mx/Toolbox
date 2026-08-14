# -*- coding: utf-8 -*-
"""对比 HD_Talent.exe 与 Talent.exe（是否运行时的精确副本）。"""
import hashlib
import os
import time

d = r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent\dist"
hd = os.path.join(d, "HD_Talent.exe")
t = os.path.join(d, "Talent.exe")

for f in (hd, t):
    if not os.path.exists(f):
        print(os.path.basename(f), "不存在")
        continue
    st = os.stat(f)
    with open(f, "rb") as fh:
        data = fh.read()
    print(f"{os.path.basename(f)}: {st.st_size} bytes, mtime={time.strftime('%H:%M:%S', time.localtime(st.st_mtime))}, md5={hashlib.md5(data).hexdigest()[:16]}")
