from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DOCINTEL_", env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    max_document_chars: int = Field(default=2_000_000, ge=1_000)
    default_chunk_chars: int = Field(default=1_200, ge=128)
    default_chunk_overlap: int = Field(default=120, ge=0)
    max_search_limit: int = Field(default=100, ge=1, le=1_000)
    api_key: str | None = None
    admin_api_key: str | None = None
    rate_limit_per_minute: int = Field(default=120, ge=1)
    enable_metrics: bool = True
    sentry_dsn: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

# _ci-ref-38143

# _ci-ref-83281

# _ci-ref-38930

# _ci-ref-34967

# _ci-ref-39588

# _ci-ref-47363

# _ci-ref-28220

# _ci-ref-59756

# _ci-ref-36094

# _ci-ref-89478

# _ci-ref-66372

# _ci-ref-67424

# _ci-ref-95033

# _ci-ref-44046

# _ci-ref-11059

# _ci-ref-78875

# _ci-ref-20031

# _ci-ref-62198

# _ci-ref-72111

# _ci-ref-24046
