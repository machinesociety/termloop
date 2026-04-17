from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class MetricsStore:
    total_requests: int = 0
    route_tiers: Counter = field(default_factory=Counter)
    cache_hits: int = 0
    rag_hits: int = 0
    _lock: Lock = field(default_factory=Lock)

    def record_request(self, route_tier: str, cache_hit: bool, rag_hit_count: int) -> None:
        with self._lock:
            self.total_requests += 1
            self.route_tiers[route_tier] += 1
            if cache_hit:
                self.cache_hits += 1
            self.rag_hits += rag_hit_count

    def summary(self) -> dict:
        with self._lock:
            return {
                "total_requests": self.total_requests,
                "cache_hits": self.cache_hits,
                "rag_hits": self.rag_hits,
                "route_tiers": dict(self.route_tiers),
            }

