import pytest

from docintel.models import DocumentIn, SavedSearchIn
from docintel.saved_searches import SavedSearchNotFound, SavedSearchStore
from docintel.service import DocumentService


def test_saved_search_store_is_owner_scoped():
    store = SavedSearchStore()
    record = store.create(SavedSearchIn(name="Invoices", query="cloud invoice"), owner="alice")
    assert store.get(record.id, owner="alice").name == "Invoices"
    with pytest.raises(SavedSearchNotFound):
        store.get(record.id, owner="bob")
    assert store.list(owner="bob") == []


def test_service_runs_saved_search_with_filters():
    service = DocumentService()
    service.ingest(DocumentIn(title="Cloud", content="cloud invoice 100", tags=["finance"]), allow_duplicate=True)
    service.ingest(DocumentIn(title="Other", content="cloud invoice 200", tags=["other"]), allow_duplicate=True)
    saved = service.create_saved_search(
        SavedSearchIn(name="Finance invoices", query="cloud invoice", tag="finance", limit=5), actor="analyst"
    )
    response = service.run_saved_search(saved.id, actor="analyst")
    assert response.total == 1
    assert response.hits[0].title == "Cloud"


def test_saved_search_api_lifecycle(client):
    created = client.post(
        "/v1/saved-searches",
        json={"name": "Invoices", "query": "cloud invoice", "limit": 3},
    )
    assert created.status_code == 201
    search_id = created.json()["id"]
    assert client.get("/v1/saved-searches").json()[0]["id"] == search_id

    updated = client.put(
        f"/v1/saved-searches/{search_id}",
        json={"name": "Cloud invoices", "query": "invoice cloud", "limit": 4},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Cloud invoices"

    missing_run = client.post("/v1/saved-searches/missing/run")
    assert missing_run.status_code == 404
    assert client.delete(f"/v1/saved-searches/{search_id}").status_code == 204
    assert client.delete(f"/v1/saved-searches/{search_id}").status_code == 404

# _ci-ref-57069

# _ci-ref-15083

# _ci-ref-28096

# _ci-ref-39110

# _ci-ref-35698

# _ci-ref-41862

# _ci-ref-34318

# _ci-ref-96235

# _ci-ref-63219

# _ci-ref-53634
