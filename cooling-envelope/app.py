"""
冷静期信封 · 桌面伴侣
入口:创建原生窗口(界面就是 web/index.html),把内核暴露给前端,
并起一个后台线程,在信封到点时发桌面通知、轻推界面刷新。

运行:
    pip install -r requirements.txt
    python app.py
"""
import os
import sys
import time
from pathlib import Path

import webview

from core.crypto import Sealer, load_or_create_key
from core.db import DB
from core.envelope import EnvelopeService
from core.notify import notify

def _resource_path(rel: str) -> str:
    """开发时相对脚本目录;被 PyInstaller 冻结后相对解包目录(sys._MEIPASS)。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


APP_DIR = Path.home() / ".cooling-envelope"          # 数据 + 密钥都在这(打包后也持久)
WEB_INDEX = _resource_path(os.path.join("web", "index.html"))

# 整个程序共享一个内核实例
_service = EnvelopeService(DB(APP_DIR / "envelopes.db"),
                           Sealer(load_or_create_key(APP_DIR)))


class Api:
    """暴露给前端的桥。前端通过 window.pywebview.api.xxx() 调用。"""

    def list(self) -> list:
        return _service.list_public()

    def seal(self, q: str, lean: str, why: str, open_at) -> dict:
        return _service.seal(q, lean, why, int(open_at))

    def open(self, id: str) -> dict:
        return _service.open(id)

    def save_verdict(self, id: str, verdict: str) -> dict:
        return _service.save_verdict(id, verdict)


def scheduler_loop(window) -> None:
    """每 20 秒看一眼:有没有信封刚到点。到点就通知一次,并轻推界面刷新。"""
    while True:
        try:
            now = int(time.time() * 1000)
            due = _service.due_for_notification(now)
            for e in due:
                notify("冷静期信封", "有一封可以拆开了 —— 情绪退潮了,回去看看那个决定。")
                _service.mark_notified(e["id"])
            if due:
                try:
                    window.evaluate_js("window.refresh && window.refresh()")
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(20)


def main() -> None:
    window = webview.create_window(
        "冷静期信封",
        str(WEB_INDEX),
        js_api=Api(),
        width=720,
        height=900,
        min_size=(420, 600),
        background_color="#F4ECD8",
    )
    # func 会在 GUI 起来之后,在独立线程里运行
    webview.start(scheduler_loop, window)


if __name__ == "__main__":
    main()
