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

# _ci-ref-70051

# _ci-ref-33741

# _ci-ref-78564

# _ci-ref-17152

# _ci-ref-23955

# _ci-ref-63101

# _ci-ref-99727

# _ci-ref-79990

# _ci-ref-37159

# _ci-ref-14190

# _ci-ref-97750

# _ci-ref-98137

# _ci-ref-56151

# _ci-ref-84455

# _ci-ref-38382

# _ci-ref-15863

# _ci-ref-35576

# _ci-ref-84270

# _ci-ref-35543

# _ci-ref-16159

# _ci-ref-79278

# _ci-ref-76077

# _ci-ref-31519

# _ci-ref-98617
