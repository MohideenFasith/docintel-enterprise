from __future__ import annotations


def test_document_lifecycle_is_exercised_through_http(client) -> None:
    created = client.post(
        "/v1/documents",
        headers={"x-actor": "integration-user"},
        json={
            "title": "Quarterly invoice",
            "content": "Cloud hosting invoice USD 4200 for August 2026.",
            "source": "integration",
            "tags": ["finance", "cloud"],
        },
    )
    assert created.status_code == 201
    document_id = created.json()["id"]

    fetched = client.get(f"/v1/documents/{document_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Quarterly invoice"

    search = client.get("/v1/search", params={"q": "cloud invoice"})
    assert search.status_code == 200
    assert search.json()["total"] >= 1
    assert search.json()["hits"][0]["document_id"] == document_id

    patched = client.patch(
        f"/v1/documents/{document_id}",
        json={"title": "Revised quarterly invoice", "tags": ["finance", "reviewed"]},
    )
    assert patched.status_code == 200
    assert "reviewed" in patched.json()["tags"]

    deleted = client.delete(f"/v1/documents/{document_id}")
    assert deleted.status_code == 204
    assert client.get(f"/v1/documents/{document_id}").status_code == 404

# _ci-ref-30591

# _ci-ref-24748

# _ci-ref-68237

# _ci-ref-98374

# _ci-ref-38574

# _ci-ref-46325

# _ci-ref-84202

# _ci-ref-69468
