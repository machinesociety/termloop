from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


@dataclass
class RagChunk:
    id: str
    text: str
    source: str


class RagStore:
    def __init__(self, root: str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "chunks.jsonl"

    def add_text(self, source: str, text: str, max_chunk_chars: int = 1200) -> list[RagChunk]:
        chunks = [text[i : i + max_chunk_chars] for i in range(0, len(text), max_chunk_chars)] or [text]
        stored: list[RagChunk] = []
        existing_ids = set()
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                payload = json.loads(line)
                existing_ids.add(payload.get("id", ""))
        with self.path.open("a", encoding="utf-8") as handle:
            for index, chunk in enumerate(chunks):
                item = RagChunk(id=f"{source}:{index}", text=chunk, source=source)
                if item.id in existing_ids:
                    continue
                handle.write(json.dumps(item.__dict__, ensure_ascii=False) + "\n")
                stored.append(item)
        return stored

    def search(self, query: str, limit: int = 3, min_score: float = 0.1) -> list[RagChunk]:
        if not self.path.exists():
            return []
        query_tokens = Counter(tokenize(query))
        query_size = max(1, sum(query_tokens.values()))
        scored: list[tuple[float, RagChunk]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            payload = json.loads(line)
            chunk = RagChunk(**payload)
            chunk_tokens = Counter(tokenize(chunk.text))
            overlap = sum(min(query_tokens[token], chunk_tokens[token]) for token in query_tokens)
            score = overlap / query_size
            if score >= min_score:
                scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:limit]]
