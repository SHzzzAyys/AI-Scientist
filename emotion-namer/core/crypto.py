"""
封蜡:把信封内容加密存盘。
开启时间之前,内容在数据库里是密文 —— 既不能通过 UI 偷看,也无法直接 grep 文件读到。
密钥存在本地 ~/.cooling-envelope/seal.key(权限 0600)。

诚实的边界:密钥在你自己机器上,所以一个铁了心、会写 Python 的你,
理论上仍能提前解开。它挡得住冲动的你,挡不住法证级的你。
若要做到"连你自己都绝对打不开",需要时间锁谜题(time-lock puzzle),见 README。
"""
import os
import stat
from pathlib import Path

from cryptography.fernet import Fernet


def load_or_create_key(app_dir: Path) -> bytes:
    app_dir.mkdir(parents=True, exist_ok=True)
    key_path = app_dir / "seal.key"
    if key_path.exists():
        return key_path.read_bytes()
    key = Fernet.generate_key()
    key_path.write_bytes(key)
    try:
        os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)  # 仅本人可读写
    except OSError:
        pass  # Windows 等平台不支持 chmod,忽略
    return key


class Sealer:
    """把文本封进蜡里 / 从蜡里取出。"""

    def __init__(self, key: bytes):
        self._fernet = Fernet(key)

    def seal(self, text: str) -> bytes:
        return self._fernet.encrypt(text.encode("utf-8"))

    def unseal(self, token: bytes) -> str:
        return self._fernet.decrypt(token).decode("utf-8")
