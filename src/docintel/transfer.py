from __future__ import annotations

import io
import json
from dataclasses import dataclass
from typing import Iterable

from pydantic import ValidationError

from .models import DocumentIn, DocumentRecord


@dataclass(frozen=True, slots=True)
class ImportErrorRow:
    line: int
    reason: str


@dataclass(slots=True)
class ImportResult:
    documents: list[DocumentIn]
    errors: list[ImportErrorRow]


def export_jsonl(documents: Iterable[DocumentRecord], *, include_content: bool = True) -> str:
    buffer = io.StringIO()
    for document in documents:
        payload = {
            "id": document.id,
            "title": document.title,
            "source": document.source,
            "tags": document.tags,
            "metadata": document.metadata,
            "version": document.version,
            "content_sha256": document.content_sha256,
            "created_at": document.created_at.isoformat(),
        }
        if include_content:
            payload["content"] = document.content
        buffer.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        buffer.write("\n")
    return buffer.getvalue()


def parse_jsonl(text: str, *, max_errors: int = 100) -> ImportResult:
    documents: list[DocumentIn] = []
    errors: list[ImportErrorRow] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            payload = json.loads(raw_line)
            documents.append(DocumentIn.model_validate(payload))
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            errors.append(ImportErrorRow(line=line_number, reason=str(exc).splitlines()[0][:300]))
            if len(errors) >= max_errors:
                break
    return ImportResult(documents=documents, errors=errors)

# _ci-ref-96252

# _ci-ref-19830

# _ci-ref-72287

# _ci-ref-40279

# _ci-ref-61495

# _ci-ref-16463

# _ci-ref-17148

# _ci-ref-30578

# _ci-ref-68491

# _ci-ref-92818

# _ci-ref-73792

# _ci-ref-41031

# _ci-ref-24621

# _ci-ref-79798

# _ci-ref-22934

# _ci-ref-84511

# _ci-ref-89391

# _ci-ref-84148

# _ci-ref-66164

# _ci-ref-88390

# _ci-ref-35891

# _ci-ref-37462

# _ci-ref-93780

# _ci-ref-53412

# _ci-ref-24201

# _ci-ref-10481

# _ci-ref-27111

# _ci-ref-38697

# _ci-ref-54285

# _ci-ref-81707
