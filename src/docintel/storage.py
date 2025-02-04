from __future__ import annotations

from copy import deepcopy
from threading import RLock

from .errors import DocumentNotFound
from .models import Chunk, DocumentRecord, DocumentStatus, ExtractedMetadata, utcnow


class InMemoryDocumentStore:
    """Thread-safe repository used by the default self-contained deployment.

    The interface intentionally mirrors methods a SQL-backed adapter would expose,
    which keeps service logic independent from persistence details.
    """

    def __init__(self) -> None:
        self._documents: dict[str, DocumentRecord] = {}
        self._chunks: dict[str, list[Chunk]] = {}
        self._hash_to_id: dict[str, str] = {}
        self._lock = RLock()

    def insert(self, record: DocumentRecord, chunks: list[Chunk]) -> DocumentRecord:
        with self._lock:
            self._documents[record.id] = deepcopy(record)
            self._chunks[record.id] = deepcopy(chunks)
            self._hash_to_id[record.content_sha256] = record.id
            return deepcopy(record)

    def get(self, document_id: str, *, include_deleted: bool = False) -> DocumentRecord:
        with self._lock:
            record = self._documents.get(document_id)
            if record is None or (record.status == DocumentStatus.DELETED and not include_deleted):
                raise DocumentNotFound(document_id)
            return deepcopy(record)

    def get_chunks(self, document_id: str) -> list[Chunk]:
        self.get(document_id)
        with self._lock:
            return deepcopy(self._chunks.get(document_id, []))

    def find_by_hash(self, content_sha256: str) -> DocumentRecord | None:
        with self._lock:
            document_id = self._hash_to_id.get(content_sha256)
            if not document_id:
                return None
            record = self._documents.get(document_id)
            if record is None or record.status == DocumentStatus.DELETED:
                return None
            return deepcopy(record)

    def update_metadata(
        self,
        document_id: str,
        *,
        title: str | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> DocumentRecord:
        with self._lock:
            record = self._documents.get(document_id)
            if record is None or record.status == DocumentStatus.DELETED:
                raise DocumentNotFound(document_id)
            if title is not None:
                record.title = title.strip()
            if tags is not None:
                record.tags = list(tags)
            if metadata is not None:
                record.metadata = deepcopy(metadata)
            record.version += 1
            record.updated_at = utcnow()
            return deepcopy(record)


    def replace_content(
        self,
        document_id: str,
        *,
        content: str,
        content_sha256: str,
        extracted: ExtractedMetadata,
        chunks: list[Chunk],
        title: str | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> DocumentRecord:
        with self._lock:
            record = self._documents.get(document_id)
            if record is None or record.status == DocumentStatus.DELETED:
                raise DocumentNotFound(document_id)
            old_hash = record.content_sha256
            if title is not None:
                record.title = title.strip()
            if tags is not None:
                record.tags = list(tags)
            if metadata is not None:
                record.metadata = deepcopy(metadata)
            record.content = content
            record.content_sha256 = content_sha256
            record.extracted = deepcopy(extracted)
            record.chunk_count = len(chunks)
            record.version += 1
            record.updated_at = utcnow()
            self._chunks[document_id] = deepcopy(chunks)
            self._hash_to_id.pop(old_hash, None)
            self._hash_to_id[content_sha256] = document_id
            return deepcopy(record)

    def delete(self, document_id: str) -> DocumentRecord:
        with self._lock:
            record = self._documents.get(document_id)
            if record is None or record.status == DocumentStatus.DELETED:
                raise DocumentNotFound(document_id)
            record.status = DocumentStatus.DELETED
            record.version += 1
            record.updated_at = utcnow()
            self._hash_to_id.pop(record.content_sha256, None)
            return deepcopy(record)

    def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        source: str | None = None,
        tag: str | None = None,
    ) -> list[DocumentRecord]:
        with self._lock:
            records = [
                deepcopy(record)
                for record in self._documents.values()
                if record.status != DocumentStatus.DELETED
            ]
        if source is not None:
            records = [record for record in records if record.source == source]
        if tag is not None:
            records = [record for record in records if tag in record.tags]
        records.sort(key=lambda record: record.created_at, reverse=True)
        return records[offset : offset + limit]

    def count(self) -> int:
        with self._lock:
            return sum(1 for record in self._documents.values() if record.status != DocumentStatus.DELETED)

    def replace_chunks(self, document_id: str, chunks: list[Chunk]) -> None:
        with self._lock:
            if document_id not in self._documents:
                raise DocumentNotFound(document_id)
            self._chunks[document_id] = deepcopy(chunks)
            record = self._documents[document_id]
            record.chunk_count = len(chunks)
            record.version += 1
            record.updated_at = utcnow()

    def all_chunks(self) -> list[tuple[DocumentRecord, Chunk]]:
        with self._lock:
            output: list[tuple[DocumentRecord, Chunk]] = []
            for document_id, chunks in self._chunks.items():
                record = self._documents.get(document_id)
                if record is None or record.status != DocumentStatus.INDEXED:
                    continue
                for chunk in chunks:
                    output.append((deepcopy(record), deepcopy(chunk)))
            return output

# _ci-ref-87814

# _ci-ref-41034

# _ci-ref-15235

# _ci-ref-97988

# _ci-ref-96623

# _ci-ref-34671

# _ci-ref-79526
