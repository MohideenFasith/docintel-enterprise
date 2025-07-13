from docintel.batch import BatchIngestor
from docintel.models import DocumentIn
from docintel.service import DocumentService


def test_batch_ingest_tracks_success_and_duplicate_failure():
    ingestor = BatchIngestor(DocumentService())
    result = ingestor.ingest([
        DocumentIn(title="A", content="same"),
        DocumentIn(title="B", content="same"),
        DocumentIn(title="C", content="different"),
    ])
    assert len(result.succeeded) == 2
    assert len(result.failed) == 1
    assert result.failed[0].index == 1


def test_batch_stop_on_error():
    ingestor = BatchIngestor(DocumentService())
    result = ingestor.ingest([
        DocumentIn(title="A", content="same"),
        DocumentIn(title="B", content="same"),
        DocumentIn(title="C", content="not reached"),
    ], stop_on_error=True)
    assert len(result.succeeded) == 1
    assert len(result.failed) == 1

# _ci-ref-13515

# _ci-ref-23624

# _ci-ref-34688

# _ci-ref-81786

# _ci-ref-81802

# _ci-ref-27548

# _ci-ref-21239

# _ci-ref-56544

# _ci-ref-35369

# _ci-ref-66980

# _ci-ref-91830

# _ci-ref-64555

# _ci-ref-69241

# _ci-ref-13250

# _ci-ref-83024

# _ci-ref-31514

# _ci-ref-76144

# _ci-ref-37575

# _ci-ref-42591

# _ci-ref-14851

# _ci-ref-84481

# _ci-ref-21759

# _ci-ref-22221

# _ci-ref-66485

# _ci-ref-84897
