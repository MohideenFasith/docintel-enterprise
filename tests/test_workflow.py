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

# _ci-ref-66260

# _ci-ref-46302

# _ci-ref-52179

# _ci-ref-31319

# _ci-ref-27614

# _ci-ref-56567

# _ci-ref-55134

# _ci-ref-76967

# _ci-ref-18239

# _ci-ref-90634

# _ci-ref-51383

# _ci-ref-75700

# _ci-ref-13418

# _ci-ref-13728

# _ci-ref-85963

# _ci-ref-40704

# _ci-ref-99707

# _ci-ref-22032

# _ci-ref-12174

# _ci-ref-23819

# _ci-ref-93586

# _ci-ref-13796

# _ci-ref-14427

# _ci-ref-60123

# _ci-ref-55214

# _ci-ref-42072

# _ci-ref-39651

# _ci-ref-19753

# _ci-ref-87704

# _ci-ref-20180

# _ci-ref-15789

# _ci-ref-16652

# _ci-ref-65452
