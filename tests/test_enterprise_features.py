from datetime import datetime, timedelta, timezone

import pytest

from docintel.annotations import AnnotationStore
from docintel.collections import CollectionStore
from docintel.extraction import extract_metadata
from docintel.models import DocumentRecord, DocumentStatus
from docintel.pagination import decode_cursor, encode_cursor
from docintel.redaction import RedactionKind, Redactor
from docintel.retention import RetentionPolicy, select_expired
from docintel.tenancy import QuotaExceeded, TenantQuota, TenantQuotaManager
from docintel.transfer import export_jsonl, parse_jsonl
from docintel.versioning import VersionStore
from docintel.webhooks import WebhookRegistry


def make_record(doc_id="doc_1", created_at=None):
    return DocumentRecord(
        id=doc_id,
        title="Invoice",
        content="line one\nline two",
        source="email",
        tags=["finance"],
        metadata={"department": "ap"},
        extracted=extract_metadata("line one\nline two"),
        status=DocumentStatus.INDEXED,
        content_sha256="a" * 64,
        created_at=created_at or datetime.now(timezone.utc),
    )


def test_cursor_round_trip_and_invalid():
    assert decode_cursor(encode_cursor(42)).offset == 42
    assert decode_cursor(None).offset == 0
    with pytest.raises(ValueError):
        decode_cursor("not-a-cursor")


def test_redaction_scans_multiple_pii_types():
    redactor = Redactor()
    result = redactor.redact("Email a@example.com, card 4111 1111 1111 1111, ip 192.168.1.1")
    kinds = {item.kind for item in result.redactions}
    assert RedactionKind.EMAIL in kinds
    assert RedactionKind.CREDIT_CARD in kinds
    assert RedactionKind.IPV4 in kinds
    assert "a@example.com" not in result.text


def test_redactor_ignores_invalid_card_and_ip():
    result = Redactor({RedactionKind.CREDIT_CARD, RedactionKind.IPV4}).scan("number 1234 5678 9012 3456 and 999.999.1.1")
    assert result == []


def test_collection_membership_and_uniqueness():
    store = CollectionStore()
    collection = store.create("Finance", "finance docs")
    assert store.add_document(collection.id, "doc_1").document_ids == {"doc_1"}
    assert store.remove_document(collection.id, "doc_1").document_ids == set()
    with pytest.raises(ValueError):
        store.create("finance")


def test_annotations_create_update_delete():
    store = AnnotationStore()
    annotation = store.create("doc_1", "alice", "needs review", {"Urgent"})
    assert annotation.labels == {"urgent"}
    updated = store.update(annotation.id, body="approved", labels={"done"})
    assert updated.body == "approved"
    assert store.list_for_document("doc_1")[0].labels == {"done"}
    store.delete(annotation.id)
    assert store.list_for_document("doc_1") == []


def test_version_store_capture_and_lookup():
    store = VersionStore()
    first = make_record()
    store.capture(first)
    second = first.model_copy(update={"version": 2, "title": "Updated"})
    store.capture(second)
    assert [version.version for version in store.list(first.id)] == [1, 2]
    assert store.get(first.id, 2).title == "Updated"


def test_tenant_quota_reserve_release():
    manager = TenantQuotaManager()
    manager.configure("acme", TenantQuota(max_documents=1, max_total_chars=10))
    assert manager.reserve_document("acme", 8).documents == 1
    with pytest.raises(QuotaExceeded):
        manager.reserve_document("acme", 1)
    assert manager.release_document("acme", 8).documents == 0


def test_webhook_registration_signing_and_retry():
    registry = WebhookRegistry()
    endpoint = registry.register("https://hooks.example.com/docintel", "a" * 20, {"document.created"})
    deliveries = registry.enqueue("document.created", {"id": "doc_1"})
    assert len(deliveries) == 1
    assert registry.sign(endpoint.id, {"id": "doc_1"}).startswith("sha256=")
    failed = registry.mark_failure(deliveries[0].id, "timeout")
    assert failed.attempt == 1
    assert failed.last_error == "timeout"


def test_retention_policy_selection():
    old = make_record(created_at=datetime.now(timezone.utc) - timedelta(days=100))
    recent = make_record("doc_2")
    policy = RetentionPolicy(name="90d-finance", max_age_days=90, sources=frozenset({"email"}), required_tags=frozenset({"finance"}))
    assert select_expired([old, recent], [policy]) == {"doc_1": "90d-finance"}


def test_jsonl_export_and_import_validation():
    text = export_jsonl([make_record()])
    assert '"title": "Invoice"' in text
    parsed = parse_jsonl('{"title":"A","content":"body"}\nnot-json\n')
    assert len(parsed.documents) == 1
    assert parsed.errors[0].line == 2
