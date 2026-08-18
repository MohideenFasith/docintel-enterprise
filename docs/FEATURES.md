# Feature map

| Area | Module | Behavior |
|---|---|---|
| Ingestion | `service.py`, `batch.py` | validation, duplicate detection, batch outcomes |
| Processing | `extraction.py`, `chunking.py` | entity extraction, boundary-aware overlapping chunks |
| Search | `index.py` | BM25-style lexical scoring, filters, snippets |
| Workflow | `workflow.py` | priority rules over title, tags, and source |
| Security | `security.py`, `redaction.py` | API keys, roles, rate limiting, PII redaction |
| Governance | `audit.py`, `retention.py`, `versioning.py` | audit events, retention selection, version snapshots |
| Organization | `collections.py`, `annotations.py` | document sets and review annotations |
| Multi-tenancy | `tenancy.py` | document/character quotas |
| Integration | `webhooks.py`, `transfer.py` | signed webhooks, JSONL import/export |
| Operations | `logging_config.py`, `metrics.py` | JSON logs and Prometheus metrics |

The default process remains self-contained and requires no external database, queue, or search service. Components are separated so production implementations can replace persistence, queueing, and retrieval independently.
