"""
情绪命名器 · 桌面伴侣
入口:创建原生窗口(界面就是 web/index.html),把内核暴露给前端。

和「冷静期信封」同一套骨架(pywebview + core/ + web/),但更简单:
命名没有时间闸门,所以不需要后台调度线程。

运行:
    pip install -r requirements.txt
    python app.py
"""
import os
import sys
from pathlib import Path

import webview

from core.crypto import Sealer, load_or_create_key
from core.db import DB
from core.namer import NamerService


def _resource_path(rel: str) -> str:
    """开发时相对脚本目录;被 PyInstaller 冻结后相对解包目录(sys._MEIPASS)。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


APP_DIR = Path.home() / ".emotion-namer"          # 数据 + 密钥都在这(打包后也持久)
WEB_INDEX = _resource_path(os.path.join("web", "index.html"))

# 整个程序共享一个内核实例
_service = NamerService(DB(APP_DIR / "entries.db"),
                        Sealer(load_or_create_key(APP_DIR)))


class Api:
    """暴露给前端的桥。前端通过 window.pywebview.api.xxx() 调用。"""

    def list(self) -> list:
        return _service.list()

    def save(self, body: str, words: list, intensity: int, why: str) -> dict:
        return _service.name_it(body, words, intensity, why)

    def delete(self, id: str) -> dict:
        return _service.delete(id)


def main() -> None:
    webview.create_window(
        "情绪命名器",
        str(WEB_INDEX),
        js_api=Api(),
        width=720,
        height=900,
        min_size=(420, 600),
        background_color="#F4ECD8",
    )
    webview.start()


if __name__ == "__main__":
    main()
