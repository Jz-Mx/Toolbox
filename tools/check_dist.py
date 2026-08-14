# -*- coding: utf-8 -*-
"""检查 dist 目录真实状态与 HD_Talent.exe。"""
import os

d = r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent\dist"
print("dist 内容：")
for f in os.listdir(d):
    p = os.path.join(d, f)
    try:
        st = os.stat(p)
        print(f"  {f}: {st.st_size} bytes, mtime={st.st_mtime:.0f}")
        if f.startswith("HD"):
            with open(p, "rb") as fh:
                print("   head:", fh.read(2))
    except Exception as e:
        print(f"  {f}: ERROR {e}")
print("Talent.exe:", os.path.getsize(os.path.join(d, "Talent.exe")), "bytes")
