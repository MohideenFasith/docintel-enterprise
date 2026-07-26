from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Annotation:
    id: str
    document_id: str
    author: str
    body: str
    labels: set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)


class AnnotationStore:
    def __init__(self) -> None:
        self._annotations: dict[str, Annotation] = {}
        self._by_document: dict[str, set[str]] = {}
        self._lock = RLock()

    @staticmethod
    def _copy(item: Annotation) -> Annotation:
        return Annotation(
            id=item.id,
            document_id=item.document_id,
            author=item.author,
            body=item.body,
            labels=set(item.labels),
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    def create(self, document_id: str, author: str, body: str, labels: set[str] | None = None) -> Annotation:
        author = author.strip()
        body = body.strip()
        if not author or not body:
            raise ValueError("author and body are required")
        item = Annotation(
            id=f"ann_{uuid4().hex}",
            document_id=document_id,
            author=author,
            body=body,
            labels={label.strip().lower() for label in (labels or set()) if label.strip()},
        )
        with self._lock:
            self._annotations[item.id] = item
            self._by_document.setdefault(document_id, set()).add(item.id)
        return self._copy(item)

    def list_for_document(self, document_id: str) -> list[Annotation]:
        with self._lock:
            ids = self._by_document.get(document_id, set())
            items = [self._copy(self._annotations[item_id]) for item_id in ids]
        return sorted(items, key=lambda item: item.created_at)

    def update(self, annotation_id: str, *, body: str | None = None, labels: set[str] | None = None) -> Annotation:
        with self._lock:
            item = self._annotations.get(annotation_id)
            if item is None:
                raise KeyError(annotation_id)
            if body is not None:
                body = body.strip()
                if not body:
                    raise ValueError("body must not be blank")
                item.body = body
            if labels is not None:
                item.labels = {label.strip().lower() for label in labels if label.strip()}
            item.updated_at = _now()
            return self._copy(item)

    def delete(self, annotation_id: str) -> None:
        with self._lock:
            item = self._annotations.pop(annotation_id, None)
            if item is None:
                raise KeyError(annotation_id)
            ids = self._by_document.get(item.document_id)
            if ids is not None:
                ids.discard(annotation_id)
                if not ids:
                    self._by_document.pop(item.document_id, None)

# _ci-ref-48737

# _ci-ref-24777

# _ci-ref-66757

# _ci-ref-76655

# _ci-ref-96105

# _ci-ref-77649

# _ci-ref-92118

# _ci-ref-33388

# _ci-ref-58867

# _ci-ref-47940

# _ci-ref-62510

# _ci-ref-42933

# _ci-ref-97983

# _ci-ref-93637

# _ci-ref-95720

# _ci-ref-17708

# _ci-ref-39127

# _ci-ref-26401

# _ci-ref-35304

# _ci-ref-93720

# _ci-ref-26784

# _ci-ref-67927

# _ci-ref-27195

# _ci-ref-47627

# _ci-ref-72338

# _ci-ref-77051

# _ci-ref-11865

# _ci-ref-36496

# _ci-ref-36293

# _ci-ref-30066

# _ci-ref-70754

# _ci-ref-77829

# _ci-ref-53992

# _ci-ref-13626

# _ci-ref-27813

# _ci-ref-66645

# _ci-ref-87125

# _ci-ref-54388

# _ci-ref-52412

# _ci-ref-87433

# _ci-ref-10999

# _ci-ref-79453

# _ci-ref-66186

# _ci-ref-93463

# _ci-ref-48537
