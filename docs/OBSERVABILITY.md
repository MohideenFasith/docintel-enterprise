# Observability

DocIntel configures application-wide JSON logging with `python-json-logger`. Request middleware emits `request_started` and `request_finished` events with `request_id`, `actor`, method, path, and status metadata. Supplying `X-Request-ID` preserves an upstream correlation identifier; otherwise the service generates one and returns it on the response.

`GET /metrics` exposes Prometheus-compatible counters when `DOCINTEL_ENABLE_METRICS=true`. `/v1/health` is a liveness check and `/v1/ready` reports service statistics for readiness probes.

Production exception tracking uses the Sentry SDK. Set `DOCINTEL_SENTRY_DSN` to enable it; leaving the value blank is an explicit no-op. Unhandled FastAPI exceptions are logged with stack traces and are passed to Sentry together with the request id. Default PII transmission is disabled.

# _ci-ref-38091
