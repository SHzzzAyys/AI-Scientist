# -*- mode: python ; coding: utf-8 -*-
"""
情绪命名器 · PyInstaller 打包配置(单文件夹 / onedir),与冷静期信封同一套打法。

    pip install pyinstaller
    pyinstaller emotion_namer.spec

产物在 dist/ 里:
  - macOS   → dist/情绪命名器.app
  - Windows → dist/EmotionNamer/EmotionNamer.exe(整个文件夹一起分发)
  - Linux   → dist/EmotionNamer/EmotionNamer

几点须知(同家族 README):
  - PyInstaller 不能跨平台编译:要哪个平台的包,就在哪个平台上打。
  - 单文件夹(onedir)对 pywebview 更稳(尤其 Windows 的 WebView2 加载器)。
  - 图标已内置在 assets/(icon.icns / icon.ico),下面按平台自动选用;想换图替换同名文件。
  - Apple Silicon 想要原生/通用包:把 target_arch 改成 "arm64" 或 "universal2"。
  - 运行时若报某后端模块缺失:把对应包名加进下面的 for pkg in (...) 里再打。
"""
import sys

from PyInstaller.utils.hooks import collect_submodules

# —— 各平台 webview 后端按需补齐(macOS→pyobjc,Windows→pythonnet) ——
hiddenimports = []
for pkg in ("WebKit", "Foundation", "objc", "clr"):
    try:
        hiddenimports += collect_submodules(pkg)
    except Exception:
        pass

APP_NAME = "情绪命名器" if sys.platform == "darwin" else "EmotionNamer"

ICON = None
if sys.platform == "darwin":
    ICON = "assets/icon.icns"
elif sys.platform.startswith("win"):
    ICON = "assets/icon.ico"

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[("web", "web")],          # 把界面与内置字体(web/)打进包里
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
    console=False,
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

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="情绪命名器.app",
        icon="assets/icon.icns",     # macOS 应用图标
        bundle_identifier="com.zheng.emotion-namer",
        info_plist={
            "CFBundleName": "情绪命名器",
            "CFBundleDisplayName": "情绪命名器",
            "NSHighResolutionCapable": True,
        },
    )
