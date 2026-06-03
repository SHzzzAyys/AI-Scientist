# -*- mode: python ; coding: utf-8 -*-
"""
冷静期信封 · PyInstaller 打包配置(单文件夹 / onedir)。

    pip install pyinstaller
    pyinstaller cooling_envelope.spec

产物在 dist/ 里:
  - macOS   → dist/冷静期信封.app
  - Windows → dist/CoolingEnvelope/CoolingEnvelope.exe(整个文件夹一起分发)
  - Linux   → dist/CoolingEnvelope/CoolingEnvelope

几点须知(详见 README「打包成桌面应用」):
  - PyInstaller 不能跨平台编译:要哪个平台的包,就在哪个平台上打。
  - 用单文件夹(onedir)而非单文件 —— 对 pywebview 更稳(尤其 Windows 的 WebView2 加载器)。
  - 图标已内置在 assets/(icon.icns / icon.ico),下面按平台自动选用;想换成自己的图替换同名文件即可。
  - Apple Silicon 想要原生/通用包:把 target_arch 改成 "arm64" 或 "universal2"。
  - 运行时若报某后端模块缺失(各平台偶发):把对应包名加进下面的 for pkg in (...) 里再打。
"""
import sys

from PyInstaller.utils.hooks import collect_submodules

# —— 各平台 webview 后端按需补齐 ——
# 运行时报某后端模块缺失,就把对应包名加进这里。常见来源:
#   macOS  → WebKit / Foundation / objc(pyobjc)
#   Windows→ clr(pythonnet,WebView2 加载器)
hiddenimports = []
for pkg in ("WebKit", "Foundation", "objc", "clr"):
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        pass  # 该平台没装这个后端,跳过即可

# macOS 出 .app;Windows / Linux 出同名可执行文件夹
APP_NAME = "冷静期信封" if sys.platform == "darwin" else "CoolingEnvelope"

# 图标:Windows 用 .ico,macOS 用 .icns(Linux 上 PyInstaller 忽略图标)。
# 想换成自己的图:替换 assets/ 下的 icon.icns / icon.ico 即可。
ICON = None
if sys.platform == "darwin":
    ICON = "assets/icon.icns"
elif sys.platform.startswith("win"):
    ICON = "assets/icon.ico"

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[("web", "web")],          # 把界面(web/index.html)打进包里
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                   # 窗口程序,不要弹控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,                # Apple Silicon:改 "arm64" / "universal2"
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON,                       # Windows 取 assets/icon.ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

# macOS 再包一层 .app(可拖进「应用程序」/ 程序坞)
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="冷静期信封.app",
        icon="assets/icon.icns",     # macOS 应用图标
        bundle_identifier="com.zheng.cooling-envelope",
        info_plist={
            "CFBundleName": "冷静期信封",
            "CFBundleDisplayName": "冷静期信封",
            "NSHighResolutionCapable": True,
        },
    )
