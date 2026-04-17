from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class CacheStore:
    def __init__(self, root: str, enabled: bool = True, ttl_seconds: int = 600) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.enabled = enabled
        self.ttl_seconds = ttl_seconds

    def key(self, payload: dict[str, Any]) -> str:
        normalized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        path = self.root / f"{self.key(payload)}.json"
        if not path.exists():
            return None
        envelope = json.loads(path.read_text(encoding="utf-8"))
        expires_at = envelope.get("expires_at")
        if expires_at:
            now = datetime.now(timezone.utc)
            if now >= datetime.fromisoformat(expires_at):
                path.unlink(missing_ok=True)
                return None
        return envelope["value"]

    def set(self, payload: dict[str, Any], value: dict[str, Any]) -> None:
        if not self.enabled:
            return
        path = self.root / f"{self.key(payload)}.json"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds)
        envelope = {"expires_at": expires_at.isoformat(), "value": value}
        path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
