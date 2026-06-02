"""
信封的业务逻辑 —— 也是"真封缄"的所在。

关键不变量:**开启时间之前,内容绝不离开后端。**
- list_public():锁着的信封只回 id / 时间 / 状态,不带任何内容文字。
- open():先校验 now >= open_at,过了才解密、才返回内容。
前端拿不到 = 偷看不了;数据库是密文 = grep 不出来。
"""
import json
import secrets
import time

from .crypto import Sealer
from .db import DB


def _now() -> int:
    return int(time.time() * 1000)


class EnvelopeService:
    def __init__(self, db: DB, sealer: Sealer):
        self.db = db
        self.sealer = sealer

    # —— 封缄 ——
    def seal(self, q: str, lean: str, why: str, open_at: int) -> dict:
        eid = "e" + str(_now()) + secrets.token_hex(2)
        payload = json.dumps({"q": q, "lean": lean, "why": why}, ensure_ascii=False)
        self.db.insert(eid, _now(), int(open_at), self.sealer.seal(payload))
        return {
            "id": eid,
            "createdAt": _now(),
            "openAt": int(open_at),
            "ready": _now() >= int(open_at),
            "opened": False,
        }

    # —— 信匣视图(带时间闸门)——
    def list_public(self) -> list[dict]:
        now = _now()
        out: list[dict] = []
        for r in self.db.all():
            opened = bool(r["opened"])
            item = {
                "id": r["id"],
                "createdAt": r["created_at"],
                "openAt": r["open_at"],
                "ready": now >= r["open_at"],
                "opened": opened,
            }
            if opened:  # 只有已拆开的才把内容交给前端
                content = json.loads(self.sealer.unseal(r["content"]))
                item["q"] = content["q"]
                item["lean"] = content.get("lean", "")
                item["why"] = content.get("why", "")
                if r["verdict"] is not None:
                    item["verdict"] = self.sealer.unseal(r["verdict"])
                    item["verdictAt"] = r["verdict_at"]
            out.append(item)
        return out

    # —— 开封 ——
    def open(self, id: str) -> dict:
        r = self.db.get(id)
        if not r:
            return {"error": "not_found"}
        if _now() < r["open_at"]:
            return {"error": "too_early"}  # 时间没到,蜡封不裂
        if not r["opened"]:
            self.db.set_opened(id)
        content = json.loads(self.sealer.unseal(r["content"]))
        return {
            "id": id,
            "q": content["q"],
            "lean": content.get("lean", ""),
            "why": content.get("why", ""),
        }

    # —— 落定裁决 ——
    def save_verdict(self, id: str, verdict: str) -> dict:
        self.db.set_verdict(id, self.sealer.seal(verdict), _now())
        return {"ok": True}

    # —— 给调度器用:到点且未通知过的 ——
    def due_for_notification(self, now_ms: int) -> list[dict]:
        return self.db.due_unnotified(now_ms)

    def mark_notified(self, id: str) -> None:
        self.db.mark_notified(id)
