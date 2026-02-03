
def test_collection_api_lifecycle(client):
    document = client.post("/v1/documents", json={"title": "A", "content": "collection content"}).json()
    created = client.post("/v1/collections", params={"name": "Research", "description": "Research docs"})
    assert created.status_code == 201
    collection_id = created.json()["id"]

    added = client.put(f"/v1/collections/{collection_id}/documents/{document['id']}")
    assert added.status_code == 200
    assert document["id"] in added.json()["document_ids"]

    listed = client.get("/v1/collections")
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Research"

    removed = client.delete(f"/v1/collections/{collection_id}/documents/{document['id']}")
    assert removed.status_code == 200
    assert removed.json()["document_ids"] == []

    assert client.delete(f"/v1/collections/{collection_id}").status_code == 204
    assert client.get(f"/v1/collections/{collection_id}").status_code == 404


def test_collection_rejects_duplicate_names_and_missing_documents(client):
    assert client.post("/v1/collections", params={"name": "Ops"}).status_code == 201
    assert client.post("/v1/collections", params={"name": "ops"}).status_code == 409
    collection_id = client.get("/v1/collections").json()[0]["id"]
    assert client.put(f"/v1/collections/{collection_id}/documents/missing").status_code == 404

# _ci-ref-58717

# _ci-ref-19965

# _ci-ref-20515

# _ci-ref-18302

# _ci-ref-99749

# _ci-ref-61910

# _ci-ref-82768

# _ci-ref-28781

# _ci-ref-52567

# _ci-ref-40154

# _ci-ref-73720

# _ci-ref-32571

# _ci-ref-69177

# _ci-ref-10676

# _ci-ref-82680

# _ci-ref-65850

# _ci-ref-87777

# _ci-ref-66317

# _ci-ref-28116

# _ci-ref-13676

# _ci-ref-68652

# _ci-ref-84475

# _ci-ref-84852

# _ci-ref-45282

# _ci-ref-95460

# _ci-ref-49656

# _ci-ref-22733

# _ci-ref-75838

# _ci-ref-42361
