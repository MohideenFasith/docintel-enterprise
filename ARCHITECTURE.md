# Architecture

## Goals

DocIntel is designed as a small but realistic document-processing backend that can run without external infrastructure while keeping boundaries clean enough to swap in production adapters. The application favors explicit orchestration over framework-heavy abstractions.

## Request flow

1. `api.py` validates HTTP inputs with Pydantic models.
2. `security.py` authenticates API keys, resolves a principal, and enforces a sliding-window limit.
3. `service.py` coordinates domain operations.
4. `extraction.py` derives structured metadata without mutating source text.
5. `chunking.py` creates deterministic chunk boundaries with overlap and human-friendly boundary selection.
6. `storage.py` stores immutable copies behind a thread-safe repository boundary.
7. `index.py` maintains a BM25-like inverted index and metadata filters.
8. `workflow.py` evaluates priority-ordered routing rules.
9. `audit.py` records mutating operations, while `metrics.py` exposes aggregate operational signals.

## Persistence boundary

`InMemoryDocumentStore` is the default adapter because it makes local development and tests deterministic. A SQL implementation should preserve method semantics: atomic insert/update/delete operations, copy isolation at the service boundary, and deleted-document filtering.

## Retrieval

The index tokenizes title, chunk text, and tags. Search computes a BM25-like score plus a small title-match boost. It supports source/tag filters, deterministic tie-breaking, snippets around matched terms, and targeted document removal/re-indexing.

## Security boundary

The application can run open in local development when no keys are configured. In secured mode writer/admin keys are stored only as SHA-256 digests in the authenticator and compared with constant-time equality. Admin-only workflow/audit operations are enforced separately from writer access.

## Observability

Structured JSON logs carry document IDs and outcomes. Prometheus metrics capture active document count, ingest outcomes, search request count, and search latency. `/v1/health` is process liveness; `/v1/ready` reports application statistics.

## Extension points

- SQL/PostgreSQL document store adapter
- external object storage for large source bodies
- dense embedding/vector retrieval blended with lexical ranking
- durable background queue replacing `JobQueue`
- OpenTelemetry tracing/export
- tenant-aware authorization and quotas

# _ci-ref-30837

# _ci-ref-21945

# _ci-ref-63856

# _ci-ref-50756

# _ci-ref-64627

# _ci-ref-83591

# _ci-ref-83420

# _ci-ref-93105

# _ci-ref-86928

# _ci-ref-72410

# _ci-ref-91233

# _ci-ref-38329

# _ci-ref-55593

# _ci-ref-77760

# _ci-ref-99779

# _ci-ref-60692

# _ci-ref-45785

# _ci-ref-97342

# _ci-ref-69233

# _ci-ref-28966

# _ci-ref-93313

# _ci-ref-75437
