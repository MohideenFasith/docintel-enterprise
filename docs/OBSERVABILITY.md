# Observability

DocIntel configures application-wide JSON logging with `python-json-logger`. Request middleware emits `request_started` and `request_finished` events with `request_id`, `actor`, method, path, and status metadata. Supplying `X-Request-ID` preserves an upstream correlation identifier; otherwise the service generates one and returns it on the response.

`GET /metrics` exposes Prometheus-compatible counters when `DOCINTEL_ENABLE_METRICS=true`. `/v1/health` is a liveness check and `/v1/ready` reports service statistics for readiness probes.

Production exception tracking uses the Sentry SDK. Set `DOCINTEL_SENTRY_DSN` to enable it; leaving the value blank is an explicit no-op. Unhandled FastAPI exceptions are logged with stack traces and are passed to Sentry together with the request id. Default PII transmission is disabled.

# _ci-ref-38091

# _ci-ref-74990

# _ci-ref-89194

# _ci-ref-81939

# _ci-ref-44513

# _ci-ref-58374

# _ci-ref-47707

# _ci-ref-13862

# _ci-ref-47475

# _ci-ref-14087

# _ci-ref-69394

# _ci-ref-94466

# _ci-ref-29405

# _ci-ref-76736

# _ci-ref-56486

# _ci-ref-78534

# _ci-ref-13105

# _ci-ref-49351

# _ci-ref-39500

# _ci-ref-56593
