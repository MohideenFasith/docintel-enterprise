
def test_content_revision_creates_version_and_updates_search(client):
    created = client.post(
        "/v1/documents",
        json={"title": "Runbook", "content": "old deployment procedure"},
    ).json()
    document_id = created["id"]

    patched = client.patch(
        f"/v1/documents/{document_id}",
        json={"content": "new deployment procedure with rollback", "title": "Runbook v2"},
    )
    assert patched.status_code == 200
    assert patched.json()["version"] == 2
    assert patched.json()["extracted"]["word_count"] == 5

    versions = client.get(f"/v1/documents/{document_id}/versions")
    assert versions.status_code == 200
    assert [item["version"] for item in versions.json()] == [1, 2]

    diff = client.get(
        f"/v1/documents/{document_id}/versions/diff",
        params={"from_version": 1, "to_version": 2},
    )
    assert diff.status_code == 200
    assert "-old deployment procedure" in diff.json()["diff"]
    assert "+new deployment procedure with rollback" in diff.json()["diff"]

    search = client.get("/v1/search", params={"q": "rollback"})
    assert search.status_code == 200
    assert search.json()["total"] == 1


def test_content_revision_rejects_duplicate_of_other_document(client):
    first = client.post("/v1/documents", json={"title": "One", "content": "first unique content"}).json()
    client.post("/v1/documents", json={"title": "Two", "content": "second unique content"})
    response = client.patch(f"/v1/documents/{first['id']}", json={"content": "second unique content"})
    assert response.status_code == 409


def test_missing_version_returns_404(client):
    document_id = client.post("/v1/documents", json={"title": "One", "content": "version body"}).json()["id"]
    response = client.get(
        f"/v1/documents/{document_id}/versions/diff",
        params={"from_version": 1, "to_version": 99},
    )
    assert response.status_code == 404

# _ci-ref-27342

# _ci-ref-48745

# _ci-ref-98063

# _ci-ref-34874

# _ci-ref-30366

# _ci-ref-79984

# _ci-ref-75210

# _ci-ref-29826

# _ci-ref-40396

# _ci-ref-23014

# _ci-ref-21854

# _ci-ref-79792

# _ci-ref-15987

# _ci-ref-77976

# _ci-ref-50019

# _ci-ref-72975
