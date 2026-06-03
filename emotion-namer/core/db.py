"""
命名簿的底:一个本地 SQLite 文件。
每条命名(情境 / 选中的词 / 强度 / 为什么)整体以密文 BLOB 存储。
时间戳一律用毫秒(与前端 Date.now() 对齐)。
"""
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id          TEXT PRIMARY KEY,
    created_at  INTEGER NOT NULL,
    content     BLOB    NOT NULL   -- 加密的 {body, words, intensity, why}
);
"""


class DB:
    def __init__(self, path: Path):
        self.path = str(path)
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def insert(self, id: str, created_at: int, content: bytes) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO entries (id, created_at, content) VALUES (?, ?, ?)",
                (id, created_at, content),
            )

    def all(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT * FROM entries ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def get(self, id: str) -> dict | None:
        with self._conn() as c:
            row = c.execute("SELECT * FROM entries WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def delete(self, id: str) -> None:
        with self._conn() as c:
            c.execute("DELETE FROM entries WHERE id = ?", (id,))
