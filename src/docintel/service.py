from __future__ import annotations

import hashlib
import logging
import time
from uuid import uuid4

from .annotations import Annotation, AnnotationStore
from .audit import AuditLog
from .chunking import chunk_text
from .collections import Collection, CollectionStore
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
    SearchAnalyticsSnapshot,
    SavedSearch,
    SavedSearchIn,
    IngestionPolicy,
    PolicyDecision,
    WorkflowDecision,
    WorkflowRule,
)
from .policies import IngestionPolicyEngine
from .saved_searches import SavedSearchStore
from .search_analytics import SearchAnalytics
from .settings import Settings, get_settings
from .storage import InMemoryDocumentStore
from .versioning import DocumentVersion, VersionStore
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
        policies: IngestionPolicyEngine | None = None,
        search_analytics: SearchAnalytics | None = None,
        collections: CollectionStore | None = None,
        annotations: AnnotationStore | None = None,
        versions: VersionStore | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.store = store or InMemoryDocumentStore()
        self.index = index or LexicalIndex()
        self.workflows = workflows or WorkflowRouter()
        self.audit = audit or AuditLog()
        self.metrics = metrics or Metrics()
        self.saved_searches = saved_searches or SavedSearchStore()
        self.policies = policies or IngestionPolicyEngine()
        self.search_analytics = search_analytics or SearchAnalytics()
        self.collections = collections or CollectionStore()
        self.annotations = annotations or AnnotationStore()
        self.versions = versions or VersionStore()

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
        policy_decision = self.policies.evaluate(payload, extracted)
        if not policy_decision.accepted:
            self.metrics.ingest_total.labels(outcome="policy_rejected").inc()
            self.audit.record(
                actor=actor,
                action="document.policy_reject",
                resource_type="document",
                resource_id="pending",
                outcome="rejected",
                detail={"violations": policy_decision.violations, "policies": policy_decision.matched_policies},
            )
            raise InvalidDocument("; ".join(policy_decision.violations))
        if policy_decision.add_tags:
            payload = payload.model_copy(update={"tags": sorted(set(payload.tags).union(policy_decision.add_tags))})
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
        stored = self.store.get(document_id)
        self.versions.capture(stored)
        logger.info("document ingested", extra={"document_id": document_id, "chunk_count": len(chunks), "actor": actor})
        return stored

    def get(self, document_id: str) -> DocumentRecord:
        return self.store.get(document_id)

    def list(self, *, offset: int = 0, limit: int = 50, source: str | None = None, tag: str | None = None) -> list[DocumentRecord]:
        return self.store.list(offset=offset, limit=limit, source=source, tag=tag)

    def patch(self, document_id: str, patch: DocumentPatch, *, actor: str = "anonymous") -> DocumentRecord:
        fields = patch.model_fields_set
        if "content" in fields and patch.content is not None:
            if len(patch.content) > self.settings.max_document_chars:
                raise InvalidDocument(f"document exceeds {self.settings.max_document_chars} characters")
            digest = self._content_hash(patch.content)
            duplicate = self.store.find_by_hash(digest)
            if duplicate is not None and duplicate.id != document_id:
                raise DuplicateDocument(duplicate.id)
            extracted = extract_metadata(patch.content)
            policy_payload = DocumentIn(
                title=patch.title or self.store.get(document_id).title,
                content=patch.content,
                source=self.store.get(document_id).source,
                tags=patch.tags if patch.tags is not None else self.store.get(document_id).tags,
                metadata=patch.metadata if patch.metadata is not None else self.store.get(document_id).metadata,
            )
            decision = self.policies.evaluate(policy_payload, extracted)
            if not decision.accepted:
                raise InvalidDocument("; ".join(decision.violations))
            tags = sorted(set(policy_payload.tags).union(decision.add_tags))
            chunks = chunk_text(
                document_id,
                patch.content,
                max_chars=self.settings.default_chunk_chars,
                overlap=self.settings.default_chunk_overlap,
                min_chunk_chars=min(200, self.settings.default_chunk_chars),
            )
            record = self.store.replace_content(
                document_id,
                content=patch.content,
                content_sha256=digest,
                extracted=extracted,
                chunks=chunks,
                title=patch.title if "title" in fields else None,
                tags=tags if ("tags" in fields or decision.add_tags) else None,
                metadata=patch.metadata if "metadata" in fields else None,
            )
        else:
            record = self.store.update_metadata(
                document_id,
                title=patch.title if "title" in fields else None,
                tags=patch.tags if "tags" in fields else None,
                metadata=patch.metadata if "metadata" in fields else None,
            )
            chunks = self.store.get_chunks(document_id)
        self.index.index_document(record, chunks)
        self.versions.capture(record)
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
        rounded_ms = round(took_ms, 3)
        self.search_analytics.record(normalized, results=len(hits), latency_ms=rounded_ms)
        logger.info("search completed", extra={"query": normalized, "results": len(hits), "took_ms": rounded_ms})
        return SearchResponse(query=normalized, total=len(hits), took_ms=rounded_ms, hits=hits)

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







    def list_versions(self, document_id: str) -> list[DocumentVersion]:
        self.store.get(document_id)
        return self.versions.list(document_id)

    def diff_versions(self, document_id: str, from_version: int, to_version: int) -> str:
        self.store.get(document_id)
        return self.versions.diff(document_id, from_version, to_version)

    def create_annotation(
        self, document_id: str, body: str, labels: set[str], *, actor: str
    ) -> Annotation:
        self.store.get(document_id)
        annotation = self.annotations.create(document_id, actor, body, labels)
        self.audit.record(
            actor=actor,
            action="annotation.create",
            resource_type="annotation",
            resource_id=annotation.id,
            detail={"document_id": document_id},
        )
        return annotation

    def update_annotation(
        self, annotation_id: str, *, body: str | None, labels: set[str] | None, actor: str
    ) -> Annotation:
        annotation = self.annotations.update(annotation_id, body=body, labels=labels)
        self.audit.record(
            actor=actor,
            action="annotation.update",
            resource_type="annotation",
            resource_id=annotation_id,
        )
        return annotation

    def delete_annotation(self, annotation_id: str, *, actor: str) -> None:
        self.annotations.delete(annotation_id)
        self.audit.record(
            actor=actor,
            action="annotation.delete",
            resource_type="annotation",
            resource_id=annotation_id,
        )

    def create_collection(self, name: str, description: str = "", *, actor: str) -> Collection:
        collection = self.collections.create(name, description)
        self.audit.record(
            actor=actor,
            action="collection.create",
            resource_type="collection",
            resource_id=collection.id,
        )
        return collection

    def add_document_to_collection(self, collection_id: str, document_id: str, *, actor: str) -> Collection:
        self.store.get(document_id)
        collection = self.collections.add_document(collection_id, document_id)
        self.audit.record(
            actor=actor,
            action="collection.document_add",
            resource_type="collection",
            resource_id=collection_id,
            detail={"document_id": document_id},
        )
        return collection

    def remove_document_from_collection(self, collection_id: str, document_id: str, *, actor: str) -> Collection:
        collection = self.collections.remove_document(collection_id, document_id)
        self.audit.record(
            actor=actor,
            action="collection.document_remove",
            resource_type="collection",
            resource_id=collection_id,
            detail={"document_id": document_id},
        )
        return collection

    def delete_collection(self, collection_id: str, *, actor: str) -> None:
        self.collections.delete(collection_id)
        self.audit.record(
            actor=actor,
            action="collection.delete",
            resource_type="collection",
            resource_id=collection_id,
        )

    def search_analytics_snapshot(self, *, limit: int = 20, zero_results_only: bool = False) -> SearchAnalyticsSnapshot:
        return self.search_analytics.snapshot(limit=limit, zero_results_only=zero_results_only)

    def reset_search_analytics(self, *, actor: str) -> None:
        self.search_analytics.reset()
        self.audit.record(
            actor=actor,
            action="search_analytics.reset",
            resource_type="search_analytics",
            resource_id="global",
        )

    def evaluate_ingestion_policy(self, payload: DocumentIn) -> PolicyDecision:
        return self.policies.evaluate(payload, extract_metadata(payload.content))

    def upsert_ingestion_policy(self, policy: IngestionPolicy, *, actor: str) -> IngestionPolicy:
        stored = self.policies.upsert(policy)
        self.audit.record(
            actor=actor,
            action="policy.upsert",
            resource_type="ingestion_policy",
            resource_id=stored.name,
        )
        return stored

    def delete_ingestion_policy(self, name: str, *, actor: str) -> None:
        self.policies.delete(name)
        self.audit.record(
            actor=actor,
            action="policy.delete",
            resource_type="ingestion_policy",
            resource_id=name,
        )

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
            "ingestion_policies": len(self.policies.list()),
            "collections": len(self.collections.list()),
        }

# _ci-ref-28661

# _ci-ref-61498

# _ci-ref-60738

# _ci-ref-42701

# _ci-ref-93151

# _ci-ref-29762
