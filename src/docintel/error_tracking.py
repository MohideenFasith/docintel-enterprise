from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import sentry_sdk  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional integration
    sentry_sdk = None  # type: ignore[assignment]


def configure_error_tracking(dsn: str | None, environment: str) -> bool:
    """Enable Sentry only when a DSN and the optional dependency are present."""
    if not dsn:
        return False
    if sentry_sdk is None:
        logger.warning("sentry_not_installed", extra={"environment": environment})
        return False
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        send_default_pii=False,
        traces_sample_rate=0.0,
    )
    return True


def capture_exception(error: BaseException, *, request_id: str | None = None) -> None:
    if sentry_sdk is None:
        return
    with sentry_sdk.new_scope() as scope:
        if request_id:
            scope.set_tag("request_id", request_id)
        sentry_sdk.capture_exception(error)
