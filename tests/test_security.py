import pytest

from docintel.errors import PermissionDenied, RateLimitExceeded
from docintel.security import ApiKeyAuthenticator, SlidingWindowRateLimiter


def test_authenticator_roles():
    auth = ApiKeyAuthenticator("writer-secret", "admin-secret")
    assert auth.authenticate("writer-secret").role == "writer"
    assert auth.authenticate("admin-secret").role == "admin"
    with pytest.raises(PermissionDenied):
        auth.authenticate("wrong")


def test_authenticator_open_mode_is_admin_for_self_contained_dev():
    assert ApiKeyAuthenticator().authenticate(None).role == "admin"


def test_role_requirement():
    principal = ApiKeyAuthenticator("key").authenticate("key")
    with pytest.raises(PermissionDenied):
        ApiKeyAuthenticator.require(principal, "admin")


def test_rate_limiter_window():
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=10)
    assert limiter.check("user", now=0) == 1
    assert limiter.check("user", now=1) == 0
    with pytest.raises(RateLimitExceeded):
        limiter.check("user", now=2)
    assert limiter.check("user", now=11) == 1

# _ci-ref-22712

# _ci-ref-99881

# _ci-ref-37487

# _ci-ref-91338

# _ci-ref-48558

# _ci-ref-99837

# _ci-ref-71974
