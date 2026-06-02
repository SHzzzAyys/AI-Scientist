"""
信匣的底:一个本地 SQLite 文件。
内容(content)与裁决(verdict)都以密文 BLOB 存储。
时间戳一律用毫秒(与前端 Date.now() 对齐)。
"""
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS envelopes (
    id          TEXT PRIMARY KEY,
    created_at  INTEGER NOT NULL,
    open_at     INTEGER NOT NULL,
    content     BLOB    NOT NULL,   -- 加密的 {q, lean, why}
    verdict     BLOB,               -- 加密的裁决,开启后才写入
    verdict_at  INTEGER,
    opened      INTEGER NOT NULL DEFAULT 0,
    notified    INTEGER NOT NULL DEFAULT 0
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

    def insert(self, id: str, created_at: int, open_at: int, content: bytes) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO envelopes (id, created_at, open_at, content) VALUES (?, ?, ?, ?)",
                (id, created_at, open_at, content),
            )

    def all(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT * FROM envelopes ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def get(self, id: str) -> dict | None:
        with self._conn() as c:
            row = c.execute("SELECT * FROM envelopes WHERE id = ?", (id,)).fetchone()
        return dict(row) if row else None

    def set_opened(self, id: str) -> None:
        with self._conn() as c:
            c.execute("UPDATE envelopes SET opened = 1 WHERE id = ?", (id,))

    def set_verdict(self, id: str, blob: bytes, at: int) -> None:
        with self._conn() as c:
            c.execute(
                "UPDATE envelopes SET verdict = ?, verdict_at = ? WHERE id = ?",
                (blob, at, id),
            )

    def mark_notified(self, id: str) -> None:
        with self._conn() as c:
            c.execute("UPDATE envelopes SET notified = 1 WHERE id = ?", (id,))

    def due_unnotified(self, now_ms: int) -> list[dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT id FROM envelopes WHERE open_at <= ? AND notified = 0",
                (now_ms,),
            ).fetchall()
        return [dict(r) for r in rows]
