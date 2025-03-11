# Changelog

## 0.3.1

- Enforce tracked reproducibility inputs in CI alongside lock-drift validation.
- Configure application-wide JSON logging with correlation fields and dedicated tests.
- Promote Sentry to a runtime exception-tracking integration that remains disabled when no DSN is configured.
- Reject real network connections throughout the pytest suite and add an end-to-end HTTP document lifecycle test.
- Make annotation label serialization deterministic while preserving set semantics in the domain store.

## 0.3.0

- Add owner-scoped saved searches with stored filters and executable queries.
- Add configurable ingestion policies for blocked phrases, metadata-count limits, and automatic tags.
- Add bounded search analytics with top-query and zero-result reporting plus admin reset.
- Expose collections and annotations through audited API workflows.
- Add content revisions that re-extract, re-chunk, re-index, and preserve version history with unified diffs.
- Replace ad-hoc JSON formatting with `python-json-logger`, add request correlation IDs, exception logging, and optional Sentry hooks.
- Add transitive runtime locking, lock-drift validation, Dependabot, split CI jobs, and a clean-container smoke test.

## 0.2.0

- Expand document lifecycle with update, delete, reindex, listing, and duplicate-content protection.
- Add overlap-aware chunking, entity extraction, BM25-style lexical search, source/tag filters, and snippets.
- Add API-key authentication, writer/admin roles, sliding-window rate limiting, PII redaction, and hardened container defaults.
- Add audit events, structured JSON logging, Prometheus metrics, workflow rules, collections, annotations, version snapshots, retention policies, tenant quotas, batch ingest, JSONL transfer, webhook signing/retry state, and a local job queue.
- Add pinned runtime dependencies, lint/type/coverage/security-audit CI gates, Make targets, expanded onboarding/architecture/security/operations documentation, and broad unit/API coverage.

# _ci-ref-24920

# _ci-ref-51984

# _ci-ref-26152

# _ci-ref-38752

# _ci-ref-91685

# _ci-ref-81901

# _ci-ref-40539

# _ci-ref-47810

# _ci-ref-59277

# _ci-ref-56843
