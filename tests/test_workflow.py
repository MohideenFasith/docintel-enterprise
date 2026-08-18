from docintel.extraction import extract_metadata
from docintel.models import DocumentRecord, DocumentStatus, WorkflowRule
from docintel.workflow import WorkflowRouter


def document(title="Quarterly invoice", tags=None, source="email"):
    return DocumentRecord(
        id="doc_1",
        title=title,
        content="body",
        source=source,
        tags=tags or [],
        metadata={},
        extracted=extract_metadata("body"),
        status=DocumentStatus.INDEXED,
        content_sha256="a" * 64,
    )


def test_priority_and_rule_matching():
    router = WorkflowRouter()
    router.upsert(WorkflowRule(name="fallback-finance", priority=50, any_tags=["finance"], target_queue="finance"))
    router.upsert(WorkflowRule(name="invoice", priority=10, title_contains=["invoice"], target_queue="ap"))
    decision = router.route(document(tags=["finance"]))
    assert decision.queue == "ap"
    assert decision.rule == "invoice"


def test_disabled_rule_and_default():
    router = WorkflowRouter()
    router.upsert(WorkflowRule(name="disabled", enabled=False, target_queue="blocked"))
    assert router.route(document()).queue == "general"
