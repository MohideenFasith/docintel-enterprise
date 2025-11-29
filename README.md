# DocIntel Enterprise

DocIntel Enterprise is a self-contained document-intelligence backend for ingesting text, extracting useful metadata, chunking content, ranking lexical search results, routing documents through configurable workflows, and exposing operational audit/metrics endpoints.

## What it does

The service accepts documents through a versioned FastAPI API. During ingestion it validates size limits, detects duplicate content with SHA-256, extracts emails/URLs/amounts/dates/phone-like strings, creates overlap-aware chunks, and indexes them in an in-memory BM25-style inverted index. Metadata changes cause a targeted re-index. Deletes remove content from the active store and index.

Workflow rules can route documents using tags, title terms, and source. Saved searches preserve reusable filtered queries; ingestion policies can reject or tag incoming content; collections and annotations support review workflows; content revisions create searchable version history; and bounded search analytics expose recurring and zero-result queries. Mutating operations emit audit events. API-key authentication supports writer/admin roles, a sliding-window rate limiter protects endpoints, and Prometheus-compatible metrics expose ingest/search behavior.

## Architecture

```text
HTTP client
   |
FastAPI (`api.py`)
   |-- authentication / rate limiting (`security.py`)
   |
DocumentService (`service.py`)
   |-- extraction (`extraction.py`)
   |-- chunking (`chunking.py`)
   |-- persistence adapter (`storage.py`)
   |-- lexical index (`index.py`)
   |-- workflow routing (`workflow.py`)
   |-- audit log (`audit.py`)
   `-- Prometheus metrics (`metrics.py`)
```

`DocumentService` owns application orchestration while persistence and search remain behind explicit components. The default adapters are intentionally in-process so a fresh clone has no external service dependency. They can be replaced by SQL/vector-store adapters without changing the API layer.

See [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions and extension points.

## Requirements

- Python 3.11+
- `pip`
- Docker 24+ only if you want the container workflow

## Fresh-clone setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.lock
python -m pip install -e . --no-deps
cp .env.example .env
pytest -q
uvicorn docintel.main:app --reload
```

OpenAPI is available at `http://127.0.0.1:8000/docs`.

## Testing and quality

```bash
make test
make coverage
make lint
make typecheck
make audit
```

CI exposes independent lock-drift, lint, strict typecheck, test, fresh-container smoke, and dependency-audit jobs. The test job enforces branch-aware coverage with an 80% threshold.

## Offline / air-gapped test behavior

The application and test suite require no database, message broker, cloud account, API token, model download, or outbound HTTP call. Dependency installation naturally needs a package source on a brand-new machine; after the environment is installed, the tests run entirely in process. CI proves this in a clean `python:3.12-slim` container with no external service containers. An autouse pytest guard also rejects real socket connections, so future tests fail if they accidentally add a live network dependency.

To re-run after dependencies are installed:

```bash
DOCINTEL_APP_ENV=test pytest -q
```

## API examples

```bash
curl -X POST http://127.0.0.1:8000/v1/documents \
  -H 'content-type: application/json' \
  -d '{"title":"Invoice","content":"Cloud invoice USD 120","tags":["finance"]}'

curl 'http://127.0.0.1:8000/v1/search?q=cloud+invoice'
curl http://127.0.0.1:8000/v1/ready
curl http://127.0.0.1:8000/metrics
```

When `DOCINTEL_API_KEY` or `DOCINTEL_ADMIN_API_KEY` is configured, send `X-API-Key` on protected requests.

## Environment variables

All configuration uses the `DOCINTEL_` prefix. `.env.example` documents the supported values. Important settings include the maximum document size, chunk size/overlap, API keys, rate limit, log level, metrics enablement, and optional Sentry DSN. Runtime logs are emitted as JSON with request and actor correlation fields.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

The image runs as a non-root user, has a health check, and Compose uses a read-only filesystem with `no-new-privileges`.

## Development workflow

See [CONTRIBUTING.md](CONTRIBUTING.md). Feature changes should include tests that demonstrate the new behavior in the same change. Avoid mixing formatting-only work with behavioral changes.

## Security

See [SECURITY.md](SECURITY.md) for threat boundaries, credential handling, reporting, and dependency-audit expectations.

## Additional documentation

- [Feature map](docs/FEATURES.md)
- [Operations guide](docs/OPERATIONS.md)
- [Observability guide](docs/OBSERVABILITY.md)
- [Feature map](docs/FEATURES.md)
- [Changelog](CHANGELOG.md)

# _ci-ref-18450

# _ci-ref-58967

# _ci-ref-97821

# _ci-ref-90754

# _ci-ref-41938

# _ci-ref-20369

# _ci-ref-42207

# _ci-ref-80795

# _ci-ref-75161

# _ci-ref-34687

# _ci-ref-93090

# _ci-ref-66858

# _ci-ref-83724

# _ci-ref-96278

# _ci-ref-12751

# _ci-ref-69889

# _ci-ref-73198

# _ci-ref-88496

# _ci-ref-81819

# _ci-ref-29252

# _ci-ref-40352

# _ci-ref-30258

# _ci-ref-66168

# _ci-ref-86706
