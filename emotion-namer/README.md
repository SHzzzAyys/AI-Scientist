# 情绪命名器 · 桌面伴侣

给说不清的情绪一个准确的名字。命名得越准,它越松手。

这是「冷静期信封」的家族第二件工具:同一张脸(同一套 `web/` + `core/` 骨架、
同一套 Cream 配色与内置字体),底下同样是 Python 管存储与加密。区别在于——
信封是把决定**封存到未来**,命名器是把情绪**看清在此刻**,所以没有时间闸门。

## 跑起来

```bash
pip install -r requirements.txt
python app.py
```

平台说明与「冷静期信封」一致:
- **macOS / Windows**:`pip install pywebview` 自带 webview 后端。
- **Linux**:需要系统 WebKitGTK(`sudo apt install libwebkit2gtk-4.1-dev`)或装 Qt 后端 `pip install "pywebview[qt]"`。

体验一条龙:写下此刻发生了什么 → 从六类情绪词库里挑贴近的词(可多选)→
标一下强度 → 写一句来由 → 「命名」。它会进「命名簿」,只存在你本机、且是密文。

## 它怎么工作

```
app.py            pywebview 入口:开窗口、把内核暴露给前端(无后台线程,命名不需要调度)
core/
  crypto.py       封蜡:Fernet 加密 + 本地密钥(~/.emotion-namer/seal.key)—— 与信封同款,直接复用
  db.py           命名簿的底:SQLite,每条命名以密文 BLOB 存储
  namer.py        命名逻辑:封存 / 列出 / 删除
web/
  index.html      界面(情绪词轮、强度、命名簿)
  fonts/          内置字体(与信封同一套,离线可用,SIL OFL 1.1)
```

数据与密钥都在 `~/.emotion-namer/`。

## 关于隐私

- 每条命名(情境 / 选中的词 / 强度 / 来由)整体**加密**后才落库;直接打开 `.db`、grep 都读不到原文。
- 密钥在你自己机器上(`~/.emotion-namer/seal.key`,权限 0600)。这是一本只给自己看的情绪簿。

## 打包成桌面应用

```bash
pip install pyinstaller
pyinstaller emotion_namer.spec
```

产物在 `dist/`:macOS → `情绪命名器.app`;Windows → `EmotionNamer/EmotionNamer.exe`;
Linux → `EmotionNamer/EmotionNamer`。图标已内置在 `assets/`。其余须知同「冷静期信封」的打包小节
(不能跨平台编译、onedir、签名公证留作后续)。
