"""
命名的业务逻辑。

和「冷静期信封」共用同一套封蜡(crypto)与本地存储(db)骨架,但这里没有时间闸门:
命名是为了「此刻看清」,所以存下即可读回。每条命名整体加密,数据库里是密文。
"""
import json
import secrets
import time

from .crypto import Sealer
from .db import DB


def _now() -> int:
    return int(time.time() * 1000)


class NamerService:
    def __init__(self, db: DB, sealer: Sealer):
        self.db = db
        self.sealer = sealer

    # —— 命名:把此刻封进密文 ——
    def name_it(self, body: str, words, intensity, why: str) -> dict:
        eid = "n" + str(_now()) + secrets.token_hex(2)
        payload = json.dumps(
            {
                "body": body,
                "words": list(words or []),
                "intensity": int(intensity or 0),
                "why": why,
            },
            ensure_ascii=False,
        )
        self.db.insert(eid, _now(), self.sealer.seal(payload))
        return self._public(self.db.get(eid))

    # —— 命名簿:按时间倒序 ——
    def list(self) -> list[dict]:
        return [self._public(r) for r in self.db.all()]

    # —— 删一条 ——
    def delete(self, id: str) -> dict:
        self.db.delete(id)
        return {"ok": True}

    def _public(self, r: dict) -> dict:
        c = json.loads(self.sealer.unseal(r["content"]))
        return {
            "id": r["id"],
            "createdAt": r["created_at"],
            "body": c.get("body", ""),
            "words": c.get("words", []),
            "intensity": c.get("intensity", 0),
            "why": c.get("why", ""),
        }
