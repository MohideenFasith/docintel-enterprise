import pytest

from docintel.errors import DuplicateDocument, InvalidDocument
from docintel.models import DocumentIn, DocumentPatch, WorkflowRule
from docintel.service import DocumentService
from docintel.settings import Settings


def service():
    return DocumentService(settings=Settings(max_document_chars=2_000, default_chunk_chars=250, default_chunk_overlap=25))


def test_ingest_search_patch_delete_lifecycle():
    svc = service()
    record = svc.ingest(DocumentIn(title="CUDA Notes", content="CUDA kernel fusion and paged attention.", tags=["ml"]))
    assert record.chunk_count == 1
    assert svc.search("paged attention").hits[0].document_id == record.id
    patched = svc.patch(record.id, DocumentPatch(title="GPU Notes", tags=["gpu"]))
    assert patched.title == "GPU Notes"
    assert svc.search("GPU").hits[0].document_id == record.id
    svc.delete(record.id)
    assert svc.search("CUDA").total == 0
    assert svc.stats()["documents"] == 0


def test_duplicate_content_rejected():
    svc = service()
    payload = DocumentIn(title="One", content="same content")
    svc.ingest(payload)
    with pytest.raises(DuplicateDocument):
        svc.ingest(DocumentIn(title="Two", content="same content"))


def test_oversized_document_rejected():
    svc = DocumentService(settings=Settings(max_document_chars=1_000))
    with pytest.raises(InvalidDocument):
        svc.ingest(DocumentIn(title="Large", content="x" * 1_001))


def test_workflow_route():
    svc = service()
    record = svc.ingest(DocumentIn(title="Vendor invoice", content="Amount USD 42.00", tags=["finance"]))
    svc.upsert_workflow(WorkflowRule(name="invoice", title_contains=["invoice"], target_queue="accounts-payable"))
    assert svc.route(record.id).queue == "accounts-payable"


def test_audit_records_mutations():
    svc = service()
    record = svc.ingest(DocumentIn(title="A", content="audit me"), actor="alice")
    svc.patch(record.id, DocumentPatch(title="B"), actor="alice")
    actions = [event.action for event in svc.audit.list(actor="alice")]
    assert actions == ["document.patch", "document.ingest"]

# _ci-ref-32570

# _ci-ref-59177

# _ci-ref-96765

# _ci-ref-11267

# _ci-ref-82512

# _ci-ref-73214

# _ci-ref-56598

# _ci-ref-70943

# _ci-ref-32398

# _ci-ref-14963

# _ci-ref-97394

# _ci-ref-34762

# _ci-ref-77294

# _ci-ref-84743

# _ci-ref-75002

# _ci-ref-95315

# _ci-ref-49855

# _ci-ref-41077

# _ci-ref-65407

# _ci-ref-48026

# _ci-ref-97518

# _ci-ref-36878

# _ci-ref-60741

# _ci-ref-20041

# _ci-ref-93164

# _ci-ref-26688

# _ci-ref-88145

# _ci-ref-60466

# _ci-ref-68868

# _ci-ref-68001
