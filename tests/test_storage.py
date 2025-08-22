import pytest

from docintel.errors import DocumentNotFound
from docintel.extraction import extract_metadata
from docintel.models import DocumentRecord, DocumentStatus
from docintel.storage import InMemoryDocumentStore


def make_record(doc_id="doc_a", source="api", tags=None):
    return DocumentRecord(
        id=doc_id,
        title="Example",
        content="body",
        source=source,
        tags=tags or [],
        metadata={},
        extracted=extract_metadata("body"),
        status=DocumentStatus.INDEXED,
        content_sha256=f"hash-{doc_id}",
    )


def test_insert_get_and_copy_isolation():
    store = InMemoryDocumentStore()
    store.insert(make_record(), [])
    record = store.get("doc_a")
    record.title = "mutated"
    assert store.get("doc_a").title == "Example"


def test_list_filters_source_and_tag():
    store = InMemoryDocumentStore()
    store.insert(make_record("a", source="s3", tags=["finance"]), [])
    store.insert(make_record("b", source="api", tags=["ops"]), [])
    assert [r.id for r in store.list(source="s3")] == ["a"]
    assert [r.id for r in store.list(tag="ops")] == ["b"]


def test_update_delete_and_missing():
    store = InMemoryDocumentStore()
    store.insert(make_record(), [])
    updated = store.update_metadata("doc_a", title="Changed", tags=["x"])
    assert updated.title == "Changed"
    assert updated.version == 2
    store.delete("doc_a")
    assert store.count() == 0
    with pytest.raises(DocumentNotFound):
        store.get("doc_a")

# _ci-ref-67684

# _ci-ref-75065

# _ci-ref-58741

# _ci-ref-18600

# _ci-ref-18557

# _ci-ref-85832

# _ci-ref-77388

# _ci-ref-72373

# _ci-ref-23143

# _ci-ref-21382

# _ci-ref-55838

# _ci-ref-51628

# _ci-ref-26193

# _ci-ref-13809

# _ci-ref-58551

# _ci-ref-13069

# _ci-ref-20169

# _ci-ref-31895

# _ci-ref-95563

# _ci-ref-62436

# _ci-ref-88532

# _ci-ref-75748
