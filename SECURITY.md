# Security policy

## Supported version

The current `0.2.x` line receives security fixes.

## Secrets

Never commit API keys, tokens, credentials, or real customer documents. `.env` is ignored; `.env.example` contains placeholders only. Production deployments should provide secrets through the runtime secret manager.

## API authentication

When API keys are configured, protected endpoints require `X-API-Key`. Writer access covers document operations. Admin access is required for workflow mutation and audit inspection. Authentication compares hashed keys with constant-time equality.

## Dependency hygiene

CI runs `pip-audit` against the pinned runtime dependency set. Dependency updates should be isolated changes with a green test/quality run.

## Container hardening

The runtime image uses a non-root user. The Compose example enables a read-only root filesystem and `no-new-privileges`.

## Reporting

Report suspected vulnerabilities privately to the repository owner. Include reproduction steps, affected versions, and impact. Do not include live credentials or customer data in reports.
