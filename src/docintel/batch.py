from __future__ import annotations

from dataclasses import dataclass, field

from .errors import DocIntelError
from .models import DocumentIn, DocumentRecord
from .service import DocumentService


@dataclass(slots=True)
class BatchFailure:
    index: int
    title: str
    error: str


@dataclass(slots=True)
class BatchResult:
    succeeded: list[DocumentRecord] = field(default_factory=list)
    failed: list[BatchFailure] = field(default_factory=list)


class BatchIngestor:
    def __init__(self, service: DocumentService) -> None:
        self.service = service

    def ingest(self, documents: list[DocumentIn], *, actor: str = "batch", stop_on_error: bool = False) -> BatchResult:
        result = BatchResult()
        for index, document in enumerate(documents):
            try:
                result.succeeded.append(self.service.ingest(document, actor=actor))
            except (DocIntelError, ValueError) as exc:
                result.failed.append(BatchFailure(index=index, title=document.title, error=str(exc)))
                if stop_on_error:
                    break
        return result

# _ci-ref-90750

# _ci-ref-13133

# _ci-ref-25825

# _ci-ref-77276

# _ci-ref-99803

# _ci-ref-94663

# _ci-ref-50838

# _ci-ref-47982

# _ci-ref-67917

# _ci-ref-82151

# _ci-ref-21376

# _ci-ref-28997

# _ci-ref-78389

# _ci-ref-48088

# _ci-ref-55238

# _ci-ref-23159
