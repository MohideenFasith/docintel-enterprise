import pytest

from docintel.errors import InvalidDocument
from docintel.extraction import extract_metadata
from docintel.models import DocumentIn, IngestionPolicy
from docintel.policies import IngestionPolicyEngine, PolicyNotFound
from docintel.service import DocumentService


def test_policy_engine_rejects_blocked_phrase_and_adds_tags():
    engine = IngestionPolicyEngine()
    engine.upsert(
        IngestionPolicy(
            name="finance-guard",
            require_any_tags=["finance"],
            block_phrases=["private key"],
            add_tags=["reviewed"],
        )
    )
    safe = DocumentIn(title="Invoice", content="normal invoice", tags=["finance"])
    safe_decision = engine.evaluate(safe, extract_metadata(safe.content))
    assert safe_decision.accepted is True
    assert safe_decision.add_tags == ["reviewed"]

    unsafe = safe.model_copy(update={"content": "contains PRIVATE KEY material"})
    decision = engine.evaluate(unsafe, extract_metadata(unsafe.content))
    assert decision.accepted is False
    assert "blocked phrase" in decision.violations[0]


def test_policy_limits_extracted_metadata_counts():
    engine = IngestionPolicyEngine()
    engine.upsert(IngestionPolicy(name="email-limit", max_emails=1, max_urls=0))
    payload = DocumentIn(title="Contacts", content="a@example.com b@example.com https://example.com")
    decision = engine.evaluate(payload, extract_metadata(payload.content))
    assert decision.accepted is False
    assert len(decision.violations) == 2


def test_service_applies_policy_added_tags_and_rejects_violations():
    service = DocumentService()
    service.upsert_ingestion_policy(
        IngestionPolicy(name="api-policy", source_equals="api", add_tags=["policy-applied"], block_phrases=["forbidden"]),
        actor="admin",
    )
    record = service.ingest(DocumentIn(title="Allowed", content="safe content"))
    assert "policy-applied" in record.tags
    with pytest.raises(InvalidDocument, match="blocked phrase"):
        service.ingest(DocumentIn(title="Denied", content="this is forbidden"), allow_duplicate=True)


def test_policy_api_lifecycle(client):
    policy = {
        "name": "external-guard",
        "priority": 10,
        "enabled": True,
        "source_equals": "external",
        "require_any_tags": [],
        "block_phrases": ["secret phrase"],
        "max_emails": 2,
        "max_urls": None,
        "add_tags": ["screened"],
    }
    assert client.put("/v1/ingestion-policies/external-guard", json=policy).status_code == 200
    listed = client.get("/v1/ingestion-policies")
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "external-guard"

    evaluated = client.post(
        "/v1/ingestion-policies/evaluate",
        json={"title": "External", "content": "contains secret phrase", "source": "external"},
    )
    assert evaluated.status_code == 200
    assert evaluated.json()["accepted"] is False
    assert client.delete("/v1/ingestion-policies/external-guard").status_code == 204
    assert client.delete("/v1/ingestion-policies/external-guard").status_code == 404


def test_missing_policy_raises():
    with pytest.raises(PolicyNotFound):
        IngestionPolicyEngine().get("missing")

# _ci-ref-81612

# _ci-ref-87537

# _ci-ref-87120

# _ci-ref-87028

# _ci-ref-87207

# _ci-ref-34105

# _ci-ref-62506

# _ci-ref-24141

# _ci-ref-32989

# _ci-ref-16385

# _ci-ref-73556

# _ci-ref-99816

# _ci-ref-68762

# _ci-ref-52540
