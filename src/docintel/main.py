from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from .api import router
from .error_tracking import capture_exception, configure_error_tracking
from .logging_config import configure_logging
from .security import ApiKeyAuthenticator, SlidingWindowRateLimiter
from .service import DocumentService
from .settings import Settings, get_settings

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    configure_logging(resolved.log_level)
    configure_error_tracking(resolved.sentry_dsn, resolved.app_env)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = resolved
        app.state.service = DocumentService(settings=resolved)
        app.state.authenticator = ApiKeyAuthenticator(resolved.api_key, resolved.admin_api_key)
        app.state.rate_limiter = SlidingWindowRateLimiter(resolved.rate_limit_per_minute)
        yield

    app = FastAPI(
        title="DocIntel Enterprise",
        version="0.3.0",
        description="Self-contained document intelligence backend with extraction, chunking, retrieval and workflow routing.",
        lifespan=lifespan,
    )
    app.include_router(router, prefix="/v1")

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or uuid4().hex
        request.state.request_id = request_id
        actor = request.headers.get("x-actor") or "anonymous"
        logger.info(
            "request_started",
            extra={"request_id": request_id, "actor": actor, "method": request.method, "path": request.url.path},
        )
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        logger.info(
            "request_finished",
            extra={"request_id": request_id, "actor": actor, "status_code": response.status_code},
        )
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception(request: Request, error: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.exception(
            "unhandled_exception",
            extra={"request_id": request_id, "actor": request.headers.get("x-actor") or "anonymous"},
        )
        capture_exception(error, request_id=request_id)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "request_id": request_id},
            headers={"x-request-id": request_id or ""},
        )

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        if not resolved.enable_metrics:
            return Response(status_code=404)
        return Response(app.state.service.metrics.render(), media_type="text/plain; version=0.0.4")

    return app


app = create_app()

# _ci-ref-84302

# _ci-ref-11610

# _ci-ref-88647

# _ci-ref-61497

# _ci-ref-89260

# _ci-ref-28953

# _ci-ref-92863

# _ci-ref-36772

# _ci-ref-28659

# _ci-ref-59327

# _ci-ref-44891

# _ci-ref-37292

# _ci-ref-36462

# _ci-ref-60002

# _ci-ref-74440

# _ci-ref-75627

# _ci-ref-85231

# _ci-ref-11401

# _ci-ref-87489
