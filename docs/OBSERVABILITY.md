# Observability

DocIntel emits structured JSON logs through `python-json-logger`. Every HTTP request receives an `x-request-id`; callers may provide one and the service preserves it. Request start, request finish, and unhandled exception events include the request ID and actor field so logs can be correlated across proxies and workers.

Prometheus-compatible metrics are exposed at `/metrics` when `DOCINTEL_ENABLE_METRICS=true`. Liveness and readiness are available at `/v1/health` and `/v1/ready`.

Sentry is an optional integration. Install the `observability` extra and set `DOCINTEL_SENTRY_DSN` to enable exception reporting. The default installation makes no external error-reporting calls and sends no PII.
