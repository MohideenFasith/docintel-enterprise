from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest


class Metrics:
    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        self.documents_total = Gauge(
            "docintel_documents_total",
            "Number of active documents",
            registry=self.registry,
        )
        self.ingest_total = Counter(
            "docintel_ingest_total",
            "Document ingest attempts",
            ["outcome"],
            registry=self.registry,
        )
        self.search_total = Counter(
            "docintel_search_total",
            "Search requests",
            registry=self.registry,
        )
        self.search_latency = Histogram(
            "docintel_search_seconds",
            "Search latency in seconds",
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
            registry=self.registry,
        )

    def render(self) -> bytes:
        return generate_latest(self.registry)

# _ci-ref-83956

# _ci-ref-38601

# _ci-ref-93964

# _ci-ref-16599

# _ci-ref-31094

# _ci-ref-18854

# _ci-ref-72460

# _ci-ref-30410

# _ci-ref-25203

# _ci-ref-45007

# _ci-ref-31344

# _ci-ref-81098
