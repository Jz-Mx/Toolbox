# Talent 工具箱 · 一键打包脚本
# 用法：在项目根目录执行  .\build.ps1
# 产物：dist\Talent.exe

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 1. 生成图标
python tools\make_icon.py

# 2. 打包
python -m PyInstaller --noconfirm --clean --onefile --noconsole `
  --name Talent `
  --add-data "web;web" `
  --icon "assets\talent.ico" `
  --hidden-import "clr" `
  app.py

Write-Host ""
Write-Host "✅ 打包完成：dist\Talent.exe" -ForegroundColor Green
