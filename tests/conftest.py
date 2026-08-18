from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from docintel.main import create_app
from docintel.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        app_env="test",
        max_document_chars=20_000,
        default_chunk_chars=300,
        default_chunk_overlap=30,
        rate_limit_per_minute=1_000,
    )


@pytest.fixture
def client(settings: Settings):
    with TestClient(create_app(settings)) as test_client:
        yield test_client
