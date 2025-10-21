
def test_annotations_api_lifecycle(client):
    document_id = client.post("/v1/documents", json={"title": "Review", "content": "annotation content"}).json()["id"]
    created = client.post(
        f"/v1/documents/{document_id}/annotations",
        json={"body": "Needs legal review", "labels": ["Legal", "legal", "urgent"]},
    )
    assert created.status_code == 201
    annotation_id = created.json()["id"]
    assert created.json()["labels"] == ["legal", "urgent"]

    listed = client.get(f"/v1/documents/{document_id}/annotations")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == annotation_id

    updated = client.patch(
        f"/v1/annotations/{annotation_id}",
        json={"body": "Reviewed", "labels": ["done"]},
    )
    assert updated.status_code == 200
    assert updated.json()["body"] == "Reviewed"
    assert updated.json()["labels"] == ["done"]

    assert client.delete(f"/v1/annotations/{annotation_id}").status_code == 204
    assert client.delete(f"/v1/annotations/{annotation_id}").status_code == 404


def test_annotations_require_existing_document(client):
    response = client.post("/v1/documents/missing/annotations", json={"body": "orphan"})
    assert response.status_code == 404
    assert client.get("/v1/documents/missing/annotations").status_code == 404

# _ci-ref-58280

# _ci-ref-91631

# _ci-ref-35470

# _ci-ref-22871

# _ci-ref-57118

# _ci-ref-44249

# _ci-ref-89349

# _ci-ref-88470

# _ci-ref-82569

# _ci-ref-32324

# _ci-ref-53150

# _ci-ref-28554

# _ci-ref-43036

# _ci-ref-35307

# _ci-ref-65965

# _ci-ref-94388

# _ci-ref-66618

# _ci-ref-35146

# _ci-ref-99218

# _ci-ref-34987

# _ci-ref-11118

# _ci-ref-66068

# _ci-ref-39634

# _ci-ref-51779

# _ci-ref-11195

# _ci-ref-95620

# _ci-ref-31305
