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

# _ci-ref-57241

# _ci-ref-83553

# _ci-ref-90649

# _ci-ref-11480

# _ci-ref-22137

# _ci-ref-59221

# _ci-ref-86486

# _ci-ref-69694

# _ci-ref-72230

# _ci-ref-40973

# _ci-ref-25218

# _ci-ref-81828

# _ci-ref-49953

# _ci-ref-47397

# _ci-ref-45378

# _ci-ref-57826

# _ci-ref-70997

# _ci-ref-18996

# _ci-ref-14356

# _ci-ref-80016

# _ci-ref-33581

# _ci-ref-60129

# _ci-ref-71906

# _ci-ref-34135

# _ci-ref-29435

# _ci-ref-29054

# _ci-ref-47035

# _ci-ref-63188
