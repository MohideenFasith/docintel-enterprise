from docintel.models import DocumentIn
from docintel.search_analytics import SearchAnalytics
from docintel.service import DocumentService


def test_search_analytics_normalizes_and_aggregates_queries():
    analytics = SearchAnalytics()
    analytics.record("  Cloud   Invoice ", results=3, latency_ms=10.0)
    analytics.record("cloud invoice", results=0, latency_ms=20.0)
    snapshot = analytics.snapshot()
    assert snapshot.total_searches == 2
    assert snapshot.unique_queries == 1
    assert snapshot.zero_result_searches == 1
    stat = snapshot.top_queries[0]
    assert stat.query == "cloud invoice"
    assert stat.count == 2
    assert stat.average_results == 1.5
    assert stat.average_latency_ms == 15.0


def test_zero_result_filter_and_reset():
    analytics = SearchAnalytics()
    analytics.record("known", results=2, latency_ms=1.0)
    analytics.record("missing", results=0, latency_ms=2.0)
    only_zero = analytics.snapshot(zero_results_only=True)
    assert [item.query for item in only_zero.top_queries] == ["missing"]
    analytics.reset()
    assert analytics.snapshot().total_searches == 0


def test_bounded_query_cardinality_evicts_least_frequent():
    analytics = SearchAnalytics(max_queries=2)
    analytics.record("popular", results=1, latency_ms=1.0)
    analytics.record("popular", results=1, latency_ms=1.0)
    analytics.record("rare", results=1, latency_ms=1.0)
    analytics.record("new", results=1, latency_ms=1.0)
    queries = {item.query for item in analytics.snapshot(limit=10).top_queries}
    assert "popular" in queries
    assert "new" in queries
    assert "rare" not in queries


def test_service_search_populates_analytics():
    service = DocumentService()
    service.ingest(DocumentIn(title="Invoice", content="cloud invoice"))
    service.search("cloud")
    service.search("missing")
    snapshot = service.search_analytics_snapshot()
    assert snapshot.total_searches == 2
    assert snapshot.zero_result_searches == 1


def test_search_analytics_api(client):
    client.post("/v1/documents", json={"title": "Invoice", "content": "cloud invoice"})
    client.get("/v1/search", params={"q": "cloud"})
    client.get("/v1/search", params={"q": "missing"})

    response = client.get("/v1/admin/search-analytics")
    assert response.status_code == 200
    assert response.json()["total_searches"] == 2

    zero = client.get("/v1/admin/search-analytics", params={"zero_results_only": True})
    assert [item["query"] for item in zero.json()["top_queries"]] == ["missing"]
    assert client.delete("/v1/admin/search-analytics").status_code == 204
    assert client.get("/v1/admin/search-analytics").json()["total_searches"] == 0

# _ci-ref-29326

# _ci-ref-78697

# _ci-ref-25431

# _ci-ref-96755

# _ci-ref-41958

# _ci-ref-18288

# _ci-ref-10864

# _ci-ref-30315

# _ci-ref-11498

# _ci-ref-59856

# _ci-ref-49117

# _ci-ref-16917

# _ci-ref-33593

# _ci-ref-96108

# _ci-ref-40649

# _ci-ref-18476

# _ci-ref-36025

# _ci-ref-47745

# _ci-ref-49634

# _ci-ref-20563

# _ci-ref-56809

# _ci-ref-69017

# _ci-ref-94815

# _ci-ref-14685

# _ci-ref-39656

# _ci-ref-57520
