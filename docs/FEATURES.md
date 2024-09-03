# Feature map

| Area | Module | Behavior |
|---|---|---|
| Ingestion | `service.py`, `batch.py` | validation, duplicate detection, batch outcomes |
| Processing | `extraction.py`, `chunking.py` | entity extraction, boundary-aware overlapping chunks |
| Search | `index.py`, `saved_searches.py`, `search_analytics.py` | BM25-style lexical scoring, filters, saved searches, bounded query analytics |
| Workflow | `workflow.py`, `policies.py` | priority routing plus pre-ingestion policy enforcement |
| Security | `security.py`, `redaction.py` | API keys, roles, rate limiting, PII redaction |
| Governance | `audit.py`, `retention.py`, `versioning.py` | audit events, retention selection, content revision history and diffs |
| Organization | `collections.py`, `annotations.py` | document sets and review annotations |
| Multi-tenancy | `tenancy.py` | document/character quotas |
| Integration | `webhooks.py`, `transfer.py` | signed webhooks, JSONL import/export |
| Operations | `logging_config.py`, `metrics.py` | JSON logs and Prometheus metrics |

The default process remains self-contained and requires no external database, queue, or search service. Components are separated so production implementations can replace persistence, queueing, and retrieval independently.

# _ci-ref-52827

# _ci-ref-64140
