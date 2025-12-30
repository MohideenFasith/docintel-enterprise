def test_health_and_ready(client):
    assert client.get("/v1/health").json() == {"status": "ok", "environment": "test"}
    ready = client.get("/v1/ready").json()
    assert ready["status"] == "ready"
    assert ready["documents"] == 0


def test_document_api_lifecycle(client):
    created = client.post("/v1/documents", json={"title": "Invoice", "content": "cloud invoice USD 120", "tags": ["Finance"]})
    assert created.status_code == 201
    doc = created.json()
    doc_id = doc["id"]
    assert doc["tags"] == ["finance"]
    assert client.get(f"/v1/documents/{doc_id}").status_code == 200

    search = client.get("/v1/search", params={"q": "cloud invoice"})
    assert search.status_code == 200
    assert search.json()["total"] == 1

    patched = client.patch(f"/v1/documents/{doc_id}", json={"title": "Updated Invoice"})
    assert patched.status_code == 200
    assert patched.json()["title"] == "Updated Invoice"

    deleted = client.delete(f"/v1/documents/{doc_id}")
    assert deleted.status_code == 204
    assert client.get(f"/v1/documents/{doc_id}").status_code == 404


def test_duplicate_returns_conflict(client):
    payload = {"title": "A", "content": "identical body"}
    assert client.post("/v1/documents", json=payload).status_code == 201
    response = client.post("/v1/documents", json={"title": "B", "content": "identical body"})
    assert response.status_code == 409


def test_missing_document_and_query_validation(client):
    assert client.get("/v1/documents/missing").status_code == 404
    assert client.get("/v1/search", params={"q": "x"}).status_code == 422


def test_workflow_api_and_route(client):
    doc_id = client.post("/v1/documents", json={"title": "Security report", "content": "incident", "tags": ["security"]}).json()["id"]
    rule = {
        "name": "security",
        "priority": 10,
        "any_tags": ["security"],
        "title_contains": [],
        "target_queue": "soc",
        "enabled": True,
    }
    assert client.put("/v1/workflows/security", json=rule).status_code == 200
    decision = client.get(f"/v1/documents/{doc_id}/route").json()
    assert decision["queue"] == "soc"


def test_metrics_endpoint(client):
    client.post("/v1/documents", json={"title": "Metric", "content": "metrics body"})
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "docintel_ingest_total" in response.text


def test_audit_endpoint(client):
    client.post("/v1/documents", json={"title": "Audit", "content": "audit body"})
    events = client.get("/v1/admin/audit").json()
    assert events
    assert events[0]["action"] == "document.ingest"

# _ci-ref-57329

# _ci-ref-86986

# _ci-ref-53911

# _ci-ref-46822

# _ci-ref-81855

# _ci-ref-50760

# _ci-ref-48209

# _ci-ref-21898

# _ci-ref-24933

# _ci-ref-39573

# _ci-ref-69429

# _ci-ref-40488

# _ci-ref-65702

# _ci-ref-89074

# _ci-ref-47587

# _ci-ref-91015

# _ci-ref-87857

# _ci-ref-86092

# _ci-ref-45146

# _ci-ref-38511

# _ci-ref-72566

# _ci-ref-30434

# _ci-ref-42997
