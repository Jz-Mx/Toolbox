# ✨ Talent 工具箱

一款简洁可爱的 Windows 桌面小工具箱 —— 毛玻璃质感、元气二次元风格、Q 弹交互。

## 功能一览

| 模块 | 内容 |
| --- | --- |
| 🏠 首页 | 时间问候、一言、硬件速览（CPU/内存/磁盘/网络环形图与进度条）、快捷入口 |
| 📊 监控 | CPU / 内存 / 网络实时折线图、系统信息（OS/CPU/显卡/主板/BIOS）、磁盘分区 |
| 🧰 工具 | 内存清理（EmptyWorkingSet）、临时文件扫描与清理、Top 10 进程管理、启动项一览 |
| 🎮 小玩意 | 计算器、番茄钟、颜色工具、字符统计、待办清单（本地保存） |
| 💌 关于 | 开发者信息 |

## 运行

- **免安装版**：双击 `dist/Talent.exe` 即可运行（Windows 10 / 11，需 WebView2 运行时，Win11 自带）。
- 窗口无边框，可按住顶部标题栏拖动；右上角最小化 / 关闭。

## 从源码运行

```powershell
pip install -r requirements.txt
python app.py
```

## 重新打包

```powershell
.\build.ps1
```

产物位于 `dist/Talent.exe`。

## 目录结构

```
Talent/
├── app.py              # 桌面端入口（pywebview 窗口 + 系统 API）
├── build.ps1           # 一键打包脚本
├── requirements.txt
├── assets/             # 应用图标
├── web/                # 前端（纯 HTML/CSS/JS，无外部依赖）
│   ├── index.html
│   ├── css/style.css
│   └── js/
├── tests/              # 后端单元测试（pytest）
└── tools/              # 构建辅助脚本（图标生成、验证）
```

## 技术栈

- 前端：原生 HTML / CSS / JS（毛玻璃 `backdrop-filter`、弹性动画）
- 桌面壳：pywebview 6（WebView2 内核，零依赖运行时）
- 系统数据：psutil + ctypes（EmptyWorkingSet）+ WMI
- 打包：PyInstaller 单文件

## 开发者

- QQ：`3145385062`
- 邮箱：`talent6839@gmail.com`

Made with ❤️ by Talent · 2025
