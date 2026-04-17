from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class CacheStore:
    def __init__(self, root: str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def key(self, payload: dict[str, Any]) -> str:
        normalized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        path = self.root / f"{self.key(payload)}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, payload: dict[str, Any], value: dict[str, Any]) -> None:
        path = self.root / f"{self.key(payload)}.json"
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

