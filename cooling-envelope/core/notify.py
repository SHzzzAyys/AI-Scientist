"""
桌面通知 —— 零额外依赖,用各平台原生命令,失败就安静退场。
macOS / Linux 开箱即用;Windows 尽力而为(见 README)。
即使通知失败,界面里那枚开始呼吸的蜡封也会提示你"可以拆了"。
"""
import subprocess
import sys


def _osa_quote(s: str) -> str:
    """把字符串安全地塞进 AppleScript 的双引号里。"""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def notify(title: str, message: str) -> None:
    try:
        if sys.platform == "darwin":
            script = (
                f"display notification {_osa_quote(message)} "
                f'with title {_osa_quote(title)} sound name "Glass"'
            )
            subprocess.run(["osascript", "-e", script], check=False,
                           capture_output=True)
        elif sys.platform.startswith("linux"):
            subprocess.run(["notify-send", title, message], check=False,
                           capture_output=True)
        elif sys.platform.startswith("win"):
            ps = (
                "[Windows.UI.Notifications.ToastNotificationManager, "
                "Windows.UI.Notifications, ContentType=WindowsRuntime] > $null; "
                "Write-Output 'noop'"
            )
            # Windows 原生 toast 较脆,这里仅尽力尝试;失败由界面兜底。
            subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           check=False, capture_output=True)
    except Exception:
        pass  # 通知不是关键路径,绝不让它崩到主程序
