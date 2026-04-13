from __future__ import annotations

from docintel import error_tracking


def test_sentry_is_noop_without_dsn(monkeypatch) -> None:
    called = False

    def fake_init(**kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(error_tracking.sentry_sdk, "init", fake_init)
    assert error_tracking.configure_error_tracking(None, "test") is False
    assert called is False


def test_sentry_initializes_when_dsn_is_configured(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_init(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(error_tracking.sentry_sdk, "init", fake_init)
    assert error_tracking.configure_error_tracking("https://public@example.invalid/1", "production") is True
    assert captured["environment"] == "production"
    assert captured["send_default_pii"] is False


def test_capture_exception_sets_request_id(monkeypatch) -> None:
    tags: dict[str, str] = {}
    captured: list[BaseException] = []

    class Scope:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def set_tag(self, key: str, value: str) -> None:
            tags[key] = value

    monkeypatch.setattr(error_tracking.sentry_sdk, "new_scope", lambda: Scope())
    monkeypatch.setattr(error_tracking.sentry_sdk, "capture_exception", captured.append)

    error = RuntimeError("boom")
    error_tracking.capture_exception(error, request_id="req-99")
    assert tags == {"request_id": "req-99"}
    assert captured == [error]

# _ci-ref-42748

# _ci-ref-71879

# _ci-ref-30202

# _ci-ref-78843

# _ci-ref-33254

# _ci-ref-40953

# _ci-ref-35023

# _ci-ref-20636

# _ci-ref-48559

# _ci-ref-49274

# _ci-ref-79479

# _ci-ref-27079

# _ci-ref-30142

# _ci-ref-55526

# _ci-ref-54353

# _ci-ref-59948

# _ci-ref-21535

# _ci-ref-33318

# _ci-ref-25765

# _ci-ref-13665

# _ci-ref-13337

# _ci-ref-21727

# _ci-ref-99415
