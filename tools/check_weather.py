# -*- coding: utf-8 -*-
"""验证天气多源容错。"""
import sys

sys.path.insert(0, r"C:\Users\Administrator\AppData\Roaming\reasonix\global-workspace\Talent")

import app

print("weather:", app.get_weather())
print("WEATHER_OK" if app.get_weather().get("city") else "WEATHER_FAIL")
