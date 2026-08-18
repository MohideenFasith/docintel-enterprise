from __future__ import annotations

import hashlib
import logging
import time
from uuid import uuid4

from .audit import AuditLog
from .chunking import chunk_text
from .errors import DuplicateDocument, InvalidDocument
from .extraction import extract_metadata
from .index import LexicalIndex
from .metrics import Metrics
from .models import (
    DocumentIn,
    DocumentPatch,
    DocumentRecord,
    DocumentStatus,
    SearchResponse,
    SavedSearch,
    SavedSearchIn,
    WorkflowDecision,
    WorkflowRule,
)
from .saved_searches import SavedSearchStore
from .settings import Settings, get_settings
from .storage import InMemoryDocumentStore
from .workflow import WorkflowRouter

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        store: InMemoryDocumentStore | None = None,
        index: LexicalIndex | None = None,
        workflows: WorkflowRouter | None = None,
        audit: AuditLog | None = None,
        metrics: Metrics | None = None,
        saved_searches: SavedSearchStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.store = store or InMemoryDocumentStore()
        self.index = index or LexicalIndex()
        self.workflows = workflows or WorkflowRouter()
        self.audit = audit or AuditLog()
        self.metrics = metrics or Metrics()
        self.saved_searches = saved_searches or SavedSearchStore()

    @staticmethod
    def _content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def ingest(self, payload: DocumentIn, *, actor: str = "anonymous", allow_duplicate: bool = False) -> DocumentRecord:
        if len(payload.content) > self.settings.max_document_chars:
            self.metrics.ingest_total.labels(outcome="rejected").inc()
            raise InvalidDocument(f"document exceeds {self.settings.max_document_chars} characters")
        digest = self._content_hash(payload.content)
        existing = self.store.find_by_hash(digest)
        if existing and not allow_duplicate:
            self.metrics.ingest_total.labels(outcome="duplicate").inc()
            raise DuplicateDocument(existing.id)

        document_id = f"doc_{uuid4().hex}"
        extracted = extract_metadata(payload.content)
        chunks = chunk_text(
            document_id,
            payload.content,
            max_chars=self.settings.default_chunk_chars,
            overlap=self.settings.default_chunk_overlap,
            min_chunk_chars=min(200, self.settings.default_chunk_chars),
        )
        record = DocumentRecord(
            id=document_id,
            title=payload.title,
            content=payload.content,
            source=payload.source,
            tags=payload.tags,
            metadata=payload.metadata,
            extracted=extracted,
            status=DocumentStatus.INDEXED,
            content_sha256=digest,
            chunk_count=len(chunks),
        )
        self.store.insert(record, chunks)
        self.index.index_document(record, chunks)
        self.metrics.ingest_total.labels(outcome="success").inc()
        self.metrics.documents_total.set(self.store.count())
        self.audit.record(
            actor=actor,
            action="document.ingest",
            resource_type="document",
            resource_id=document_id,
            detail={"chunks": len(chunks), "source": payload.source},
        )
        logger.info("document ingested", extra={"document_id": document_id, "chunk_count": len(chunks), "actor": actor})
        return self.store.get(document_id)

    def get(self, document_id: str) -> DocumentRecord:
        return self.store.get(document_id)

    def list(self, *, offset: int = 0, limit: int = 50, source: str | None = None, tag: str | None = None) -> list[DocumentRecord]:
        return self.store.list(offset=offset, limit=limit, source=source, tag=tag)

    def patch(self, document_id: str, patch: DocumentPatch, *, actor: str = "anonymous") -> DocumentRecord:
        fields = patch.model_fields_set
        record = self.store.update_metadata(
            document_id,
            title=patch.title if "title" in fields else None,
            tags=patch.tags if "tags" in fields else None,
            metadata=patch.metadata if "metadata" in fields else None,
        )
        chunks = self.store.get_chunks(document_id)
        self.index.index_document(record, chunks)
        self.audit.record(
            actor=actor,
            action="document.patch",
            resource_type="document",
            resource_id=document_id,
            detail={"fields": sorted(fields)},
        )
        return record

    def delete(self, document_id: str, *, actor: str = "anonymous") -> None:
        self.store.delete(document_id)
        self.index.remove_document(document_id)
        self.metrics.documents_total.set(self.store.count())
        self.audit.record(
            actor=actor,
            action="document.delete",
            resource_type="document",
            resource_id=document_id,
        )
        logger.info("document deleted", extra={"document_id": document_id, "actor": actor})

    def reindex(self, document_id: str, *, actor: str = "system") -> DocumentRecord:
        record = self.store.get(document_id)
        chunks = chunk_text(
            document_id,
            record.content,
            max_chars=self.settings.default_chunk_chars,
            overlap=self.settings.default_chunk_overlap,
            min_chunk_chars=min(200, self.settings.default_chunk_chars),
        )
        self.store.replace_chunks(document_id, chunks)
        record = self.store.get(document_id)
        self.index.index_document(record, chunks)
        self.audit.record(
            actor=actor,
            action="document.reindex",
            resource_type="document",
            resource_id=document_id,
            detail={"chunks": len(chunks)},
        )
        return record

    def search(
        self,
        query: str,
        limit: int = 10,
        *,
        tag: str | None = None,
        source: str | None = None,
    ) -> SearchResponse:
        normalized = query.strip()
        if len(normalized) < 2:
            raise ValueError("query must contain at least two characters")
        limit = min(limit, self.settings.max_search_limit)
        started = time.perf_counter()
        with self.metrics.search_latency.time():
            hits = self.index.search(normalized, limit=limit, required_tag=tag, source=source)
        self.metrics.search_total.inc()
        took_ms = (time.perf_counter() - started) * 1_000
        logger.info("search completed", extra={"query": normalized, "results": len(hits), "took_ms": round(took_ms, 3)})
        return SearchResponse(query=normalized, total=len(hits), took_ms=round(took_ms, 3), hits=hits)

    def route(self, document_id: str) -> WorkflowDecision:
        return self.workflows.route(self.store.get(document_id))

    def upsert_workflow(self, rule: WorkflowRule, *, actor: str = "anonymous") -> WorkflowRule:
        stored = self.workflows.upsert(rule)
        self.audit.record(
            actor=actor,
            action="workflow.upsert",
            resource_type="workflow",
            resource_id=stored.name,
        )
        return stored


    def create_saved_search(self, payload: SavedSearchIn, *, actor: str) -> SavedSearch:
        record = self.saved_searches.create(payload, owner=actor)
        self.audit.record(
            actor=actor,
            action="saved_search.create",
            resource_type="saved_search",
            resource_id=record.id,
        )
        return record

    def list_saved_searches(self, *, actor: str) -> list[SavedSearch]:
        return self.saved_searches.list(owner=actor)

    def run_saved_search(self, search_id: str, *, actor: str) -> SearchResponse:
        saved = self.saved_searches.get(search_id, owner=actor)
        return self.search(saved.query, saved.limit, tag=saved.tag, source=saved.source)

    def replace_saved_search(self, search_id: str, payload: SavedSearchIn, *, actor: str) -> SavedSearch:
        record = self.saved_searches.replace(search_id, payload, owner=actor)
        self.audit.record(
            actor=actor,
            action="saved_search.replace",
            resource_type="saved_search",
            resource_id=search_id,
        )
        return record

    def delete_saved_search(self, search_id: str, *, actor: str) -> None:
        self.saved_searches.delete(search_id, owner=actor)
        self.audit.record(
            actor=actor,
            action="saved_search.delete",
            resource_type="saved_search",
            resource_id=search_id,
        )

    def stats(self) -> dict:
        return {
            "documents": self.store.count(),
            "index": self.index.stats(),
            "workflows": len(self.workflows.list()),
            "saved_searches": len(self.saved_searches.list()),
        }
