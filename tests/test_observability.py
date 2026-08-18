from fastapi.testclient import TestClient

from docintel.main import create_app
from docintel.settings import Settings


def test_request_id_is_preserved(client):
    response = client.get("/v1/health", headers={"x-request-id": "req-123", "x-actor": "tester"})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-123"


def test_request_id_is_generated(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert len(response.headers["x-request-id"]) >= 16


def test_unhandled_exception_returns_stable_error_shape():
    app = create_app(Settings(app_env="test"))

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom", headers={"x-request-id": "boom-1"})
    assert response.status_code == 500
    assert response.json() == {"error": "internal_server_error", "request_id": "boom-1"}
    assert response.headers["x-request-id"] == "boom-1"
