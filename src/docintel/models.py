from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DocumentStatus(str, Enum):
    PENDING = "pending"
    INDEXED = "indexed"
    FAILED = "failed"
    DELETED = "deleted"


class DocumentIn(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1)
    source: str = Field(default="api", min_length=1, max_length=100)
    tags: list[str] = Field(default_factory=list, max_length=50)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("title", "content", "source")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for value in values:
            item = value.strip().lower()
            if item and item not in seen:
                normalized.append(item)
                seen.add(item)
        return normalized


class DocumentPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    content: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class ExtractedMetadata(BaseModel):
    emails: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    amounts: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    word_count: int = 0
    line_count: int = 0


class Chunk(BaseModel):
    id: str
    document_id: str
    ordinal: int = Field(ge=0)
    text: str
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    token_estimate: int = Field(ge=0)


class DocumentRecord(BaseModel):
    id: str
    title: str
    content: str
    source: str
    tags: list[str]
    metadata: dict[str, Any]
    extracted: ExtractedMetadata
    status: DocumentStatus = DocumentStatus.PENDING
    content_sha256: str
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    chunk_count: int = 0


class SearchHit(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    snippet: str
    score: float
    matched_terms: list[str]
    tags: list[str]


class SearchResponse(BaseModel):
    query: str
    total: int
    took_ms: float
    hits: list[SearchHit]


class WorkflowRule(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    priority: int = Field(default=100, ge=0, le=10_000)
    any_tags: list[str] = Field(default_factory=list)
    title_contains: list[str] = Field(default_factory=list)
    source_equals: str | None = None
    target_queue: str = Field(min_length=1, max_length=120)
    enabled: bool = True


class WorkflowDecision(BaseModel):
    queue: str
    rule: str | None = None
    reason: str


class AuditEvent(BaseModel):
    id: str
    actor: str
    action: str
    resource_type: str
    resource_id: str
    outcome: str
    detail: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobRecord(BaseModel):
    id: str
    kind: str
    payload: dict[str, Any]
    status: JobStatus = JobStatus.QUEUED
    attempts: int = 0
    error: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

class SavedSearchIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    query: str = Field(min_length=2, max_length=500)
    tag: str | None = Field(default=None, max_length=100)
    source: str | None = Field(default=None, max_length=100)
    limit: int = Field(default=10, ge=1, le=100)

    @field_validator("name", "query")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class SavedSearch(BaseModel):
    id: str
    owner: str
    name: str
    query: str
    tag: str | None = None
    source: str | None = None
    limit: int = Field(default=10, ge=1, le=100)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

class IngestionPolicy(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    priority: int = Field(default=100, ge=0, le=10_000)
    enabled: bool = True
    source_equals: str | None = Field(default=None, max_length=100)
    require_any_tags: list[str] = Field(default_factory=list)
    block_phrases: list[str] = Field(default_factory=list)
    max_emails: int | None = Field(default=None, ge=0, le=10_000)
    max_urls: int | None = Field(default=None, ge=0, le=10_000)
    add_tags: list[str] = Field(default_factory=list)

    @field_validator("require_any_tags", "add_tags")
    @classmethod
    def normalize_policy_tags(cls, values: list[str]) -> list[str]:
        return sorted({value.strip().lower() for value in values if value.strip()})

    @field_validator("block_phrases")
    @classmethod
    def normalize_phrases(cls, values: list[str]) -> list[str]:
        return sorted({value.strip().lower() for value in values if value.strip()})


class PolicyDecision(BaseModel):
    accepted: bool
    matched_policies: list[str] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)
    add_tags: list[str] = Field(default_factory=list)

class QueryStat(BaseModel):
    query: str
    count: int = Field(ge=1)
    zero_result_count: int = Field(ge=0)
    total_results: int = Field(ge=0)
    average_results: float = Field(ge=0.0)
    average_latency_ms: float = Field(ge=0.0)
    last_seen_at: datetime


class SearchAnalyticsSnapshot(BaseModel):
    total_searches: int = Field(ge=0)
    unique_queries: int = Field(ge=0)
    zero_result_searches: int = Field(ge=0)
    top_queries: list[QueryStat] = Field(default_factory=list)

class AnnotationIn(BaseModel):
    body: str = Field(min_length=1, max_length=10_000)
    labels: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("body")
    @classmethod
    def strip_annotation_body(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("labels")
    @classmethod
    def normalize_annotation_labels(cls, values: list[str]) -> list[str]:
        return sorted({value.strip().lower() for value in values if value.strip()})


class AnnotationPatch(BaseModel):
    body: str | None = Field(default=None, min_length=1, max_length=10_000)
    labels: list[str] | None = Field(default=None, max_length=50)

# _ci-ref-25806

# _ci-ref-44226

# _ci-ref-92710
