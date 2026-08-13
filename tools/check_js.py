# -*- coding: utf-8 -*-
"""对 web/js 下所有 JS 文件做语法检查（esprima）。"""
import glob
import os
import sys

import esprima

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web")
files = glob.glob(os.path.join(root, "**", "*.js"), recursive=True)
ok = True
for f in files:
    try:
        with open(f, encoding="utf-8") as fh:
            esprima.parseScript(fh.read())
        print("OK  ", os.path.relpath(f, root))
    except Exception as e:
        ok = False
        print("FAIL", os.path.relpath(f, root), "->", e)

print("RESULT:", "ALL_OK" if ok else "HAS_ERRORS")
sys.exit(0 if ok else 1)
