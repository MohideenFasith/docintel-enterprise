from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from .models import QueryStat, SearchAnalyticsSnapshot, utcnow


@dataclass(slots=True)
class _Accumulator:
    count: int = 0
    zero_result_count: int = 0
    total_results: int = 0
    total_latency_ms: float = 0.0
    last_seen_at = None


class SearchAnalytics:
    """Bounded in-process aggregate statistics for search behavior."""

    def __init__(self, max_queries: int = 5_000) -> None:
        if max_queries < 1:
            raise ValueError("max_queries must be positive")
        self.max_queries = max_queries
        self._items: dict[str, _Accumulator] = {}
        self._total_searches = 0
        self._zero_result_searches = 0
        self._lock = RLock()

    @staticmethod
    def normalize_query(query: str) -> str:
        return " ".join(query.lower().split())

    def record(self, query: str, *, results: int, latency_ms: float) -> None:
        key = self.normalize_query(query)
        if not key:
            return
        with self._lock:
            if key not in self._items and len(self._items) >= self.max_queries:
                victim = min(
                    self._items.items(),
                    key=lambda item: (item[1].count, item[1].last_seen_at or utcnow()),
                )[0]
                del self._items[victim]
            acc = self._items.setdefault(key, _Accumulator())
            acc.count += 1
            acc.total_results += max(0, results)
            acc.total_latency_ms += max(0.0, latency_ms)
            acc.last_seen_at = utcnow()
            self._total_searches += 1
            if results == 0:
                acc.zero_result_count += 1
                self._zero_result_searches += 1

    def _stat(self, query: str, acc: _Accumulator) -> QueryStat:
        assert acc.last_seen_at is not None
        return QueryStat(
            query=query,
            count=acc.count,
            zero_result_count=acc.zero_result_count,
            total_results=acc.total_results,
            average_results=round(acc.total_results / acc.count, 3),
            average_latency_ms=round(acc.total_latency_ms / acc.count, 3),
            last_seen_at=acc.last_seen_at,
        )

    def snapshot(self, *, limit: int = 20, zero_results_only: bool = False) -> SearchAnalyticsSnapshot:
        limit = max(1, min(limit, 500))
        with self._lock:
            pairs = list(self._items.items())
            total_searches = self._total_searches
            zero_result_searches = self._zero_result_searches
        if zero_results_only:
            pairs = [(query, acc) for query, acc in pairs if acc.zero_result_count > 0]
        pairs.sort(key=lambda item: (-item[1].count, -item[1].zero_result_count, item[0]))
        return SearchAnalyticsSnapshot(
            total_searches=total_searches,
            unique_queries=len(self._items),
            zero_result_searches=zero_result_searches,
            top_queries=[self._stat(query, acc) for query, acc in pairs[:limit]],
        )

    def reset(self) -> None:
        with self._lock:
            self._items.clear()
            self._total_searches = 0
            self._zero_result_searches = 0
