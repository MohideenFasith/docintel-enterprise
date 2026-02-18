from __future__ import annotations

import logging

import sentry_sdk

logger = logging.getLogger(__name__)


def configure_error_tracking(dsn: str | None, environment: str) -> bool:
    """Configure Sentry when a DSN is present; remain a no-op otherwise."""
    if not dsn:
        logger.info(
            "error_tracking_disabled",
            extra={"environment": environment, "provider": "sentry"},
        )
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        send_default_pii=False,
        traces_sample_rate=0.0,
    )
    logger.info(
        "error_tracking_enabled",
        extra={"environment": environment, "provider": "sentry"},
    )
    return True


def capture_exception(error: BaseException, *, request_id: str | None = None) -> None:
    """Capture an unhandled error and attach the request id for correlation."""
    with sentry_sdk.new_scope() as scope:
        if request_id:
            scope.set_tag("request_id", request_id)
        sentry_sdk.capture_exception(error)

# _ci-ref-27451

# _ci-ref-26142

# _ci-ref-67367

# _ci-ref-98940

# _ci-ref-32973

# _ci-ref-70142

# _ci-ref-90213

# _ci-ref-49229

# _ci-ref-76088

# _ci-ref-14141

# _ci-ref-24336

# _ci-ref-74447

# _ci-ref-15697

# _ci-ref-88494

# _ci-ref-61060

# _ci-ref-66223

# _ci-ref-32751

# _ci-ref-92223

# _ci-ref-59063

# _ci-ref-96944

# _ci-ref-46194

# _ci-ref-82468

# _ci-ref-60532

# _ci-ref-94125

# _ci-ref-13068

# _ci-ref-62575

# _ci-ref-70806

# _ci-ref-24249

# _ci-ref-62963

# _ci-ref-18913

# _ci-ref-73945

# _ci-ref-56969

# _ci-ref-18834
