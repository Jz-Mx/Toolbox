# -*- coding: utf-8 -*-
"""对比 HD_Talent.exe 与 Talent.exe（来源排查）。"""
import hashlib
import os

d = r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent\dist"
hd = os.path.join(d, "HD_Talent.exe")
t = os.path.join(d, "Talent.exe")

for f in (hd, t):
    st = os.stat(f)
    with open(f, "rb") as fh:
        data = fh.read()
    print(f"{os.path.basename(f)}: {st.st_size} bytes, mtime={st.st_mtime:.0f}, md5={hashlib.md5(data).hexdigest()[:12]}, head={data[:16].hex()}")
