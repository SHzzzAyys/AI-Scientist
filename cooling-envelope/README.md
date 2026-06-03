# 冷静期信封 · 桌面伴侣

把此刻的决定先封起来,交给明天那个情绪已经退潮的你来拍板。

这是一个本地优先的桌面小程序:界面就是一套 HTML/CSS(和 zheng.com 主页同一张脸),
Python 在底下管存储、加密、调度和桌面通知。

## 跑起来

```bash
pip install -r requirements.txt
python app.py
```

平台说明:
- **macOS / Windows**:`pip install pywebview` 会自带所需的 webview 后端,直接能跑。
- **Linux**:需要系统的 WebKitGTK(如 `sudo apt install libwebkit2gtk-4.1-dev`)或装 Qt 后端 `pip install "pywebview[qt]"`。
- 桌面通知:macOS / Linux 开箱即用;Windows 为尽力而为。无论通知是否成功,界面里那枚开始呼吸的蜡封都会提示"可以拆了"。

想快速体验整条链路:写一个决定 → 选「测试·1 分钟」→ 封缄 → 约一分钟后会收到通知 → 点蜡封,蜡裂开,写下退潮后的裁决。

## 它怎么工作

```
app.py            pywebview 入口:开窗口、把内核暴露给前端、起后台通知线程
core/
  crypto.py       封蜡:Fernet 加密 + 本地密钥(~/.cooling-envelope/seal.key)
  db.py           信匣的底:SQLite,内容以密文 BLOB 存储
  envelope.py     信封逻辑 + “真封缄”不变量(到点前内容不离开后端)
  notify.py       跨平台桌面通知(零额外依赖)
web/index.html    界面(蜡封、字体、配色都在这)
```

数据与密钥都在 `~/.cooling-envelope/`。

## 关于“封”有多真

- 开启时间之前:列表接口**不返回**任何内容文字,`open()` 会直接拒绝。所以通过界面偷看不到。
- 内容在数据库里是**密文**,直接打开 `.db` 文件、grep 都读不到原文。
- 诚实的边界:密钥就在你自己机器上,所以一个铁了心、会写 Python 的你,理论上仍能提前强行解开。
  它挡得住冲动的你,挡不住法证级的你。
- 若想做到“连你自己都绝对打不开”,那需要**时间锁谜题**(time-lock puzzle,如 Rivest 的顺序平方):
  把内容用一个只有持续算 N 秒才能解出的密钥加密。代价是难度要按 CPU 标定、跨机器不可靠、长时锁几乎不可行,
  所以这里没用它。可作为以后“想更狠一点”的方向。

## 打包成桌面应用(双击即开)

```bash
pip install pyinstaller
pyinstaller cooling_envelope.spec
```

产物在 `dist/` 里:
- **macOS** → `dist/冷静期信封.app`(可拖进「应用程序」/ 程序坞)
- **Windows** → `dist/CoolingEnvelope/`,里面是 `CoolingEnvelope.exe`(整个文件夹一起分发,或打成 zip)
- **Linux** → `dist/CoolingEnvelope/CoolingEnvelope`

几个要知道的:
- **PyInstaller 不能跨平台编译**。要 mac 的 `.app` 就在 mac 上打,要 `.exe` 就在 Windows 上打,要 Linux 版就在 Linux 上打。
- 配置用的是**单文件夹(onedir)**而非单文件——对 pywebview 更稳(尤其 Windows 的 WebView2 加载器)。
- 图标已内置在 `assets/`(`icon.icns` / `icon.ico`),spec 按平台自动选用;想换成自己的图,替换 `assets/` 下同名文件即可。
- Apple Silicon 想要原生或通用包:把 spec 里的 `target_arch` 改成 `"arm64"` 或 `"universal2"`。
- **如果运行时报某个后端模块缺失**(各平台偶发):在 spec 顶部那个 `for pkg in (...)` 里把对应包加进去再打。常见来源:macOS 的 `WebKit` / `Foundation`(pyobjc),Windows 的 `clr`(pythonnet)。
- macOS 上别人下载你的 `.app` 可能被 Gatekeeper 拦。自己用:右键「打开」放行;要给别人用得做签名 + 公证(codesign / notarytool),可作为以后的步骤。

## 下一步(没做、留着)

- 给 `.app` / `.exe` 做**签名 + 公证**(codesign / notarytool;需 Apple 开发者账号),让别人下载后也是双击即开,不被 Gatekeeper 拦。(图标已内置,见 `assets/`。)
- 这套外壳就是家族的脸:`情绪命名器` 等后续工具可以直接复用同一套 `web/` + `core/` 骨架。
