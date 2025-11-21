# Operations guide

## Health model

`/v1/health` is a lightweight process liveness probe. `/v1/ready` returns application-level counts for active documents, indexed chunks/terms, and workflow rules. `/metrics` exposes Prometheus text format when metrics are enabled.

## Logging

Application logs are emitted as compact JSON to standard output. Ingest, delete, and search operations include identifiers/outcomes suitable for centralized log ingestion. Configure the threshold with `DOCINTEL_LOG_LEVEL`.

## Rate limiting

The built-in limiter is a per-process sliding window intended for self-contained deployments. Distributed deployments should replace it with a shared Redis or gateway-backed limiter while retaining the same principal key semantics.

## Backups and persistence

The default store is deliberately in-memory. Production adapters should persist source bodies and metadata, preserve soft-delete semantics, and rebuild the lexical index from the authoritative store. JSONL export provides a portable interchange format for small deployments.

## Dependency updates

Keep runtime pins in `requirements.lock` aligned with `pyproject.toml`. Run tests, type checking, lint, and `pip-audit` in the same change as dependency updates.

# _ci-ref-52762

# _ci-ref-73499

# _ci-ref-21847

# _ci-ref-72684

# _ci-ref-67047

# _ci-ref-54222

# _ci-ref-45633

# _ci-ref-85527

# _ci-ref-45887

# _ci-ref-97932

# _ci-ref-22844

# _ci-ref-82562

# _ci-ref-13251

# _ci-ref-72230

# _ci-ref-61355

# _ci-ref-36013

# _ci-ref-69097

# _ci-ref-67105

# _ci-ref-64521

# _ci-ref-37614

# _ci-ref-75106

# _ci-ref-58660

# _ci-ref-28728
