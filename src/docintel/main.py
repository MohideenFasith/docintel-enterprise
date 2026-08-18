from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Response

from .api import router
from .logging_config import configure_logging
from .security import ApiKeyAuthenticator, SlidingWindowRateLimiter
from .service import DocumentService
from .settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    configure_logging(resolved.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = resolved
        app.state.service = DocumentService(settings=resolved)
        app.state.authenticator = ApiKeyAuthenticator(resolved.api_key, resolved.admin_api_key)
        app.state.rate_limiter = SlidingWindowRateLimiter(resolved.rate_limit_per_minute)
        yield

    app = FastAPI(
        title="DocIntel Enterprise",
        version="0.2.0",
        description="Self-contained document intelligence backend with extraction, chunking, retrieval and workflow routing.",
        lifespan=lifespan,
    )
    app.include_router(router, prefix="/v1")

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        if not resolved.enable_metrics:
            return Response(status_code=404)
        return Response(app.state.service.metrics.render(), media_type="text/plain; version=0.0.4")

    return app


app = create_app()
