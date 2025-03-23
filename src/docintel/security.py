from __future__ import annotations

import hashlib
import hmac
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from threading import RLock

from .errors import PermissionDenied, RateLimitExceeded


@dataclass(frozen=True, slots=True)
class Principal:
    name: str
    role: str


class ApiKeyAuthenticator:
    def __init__(self, api_key: str | None = None, admin_api_key: str | None = None) -> None:
        self._api_key_digest = self._digest(api_key) if api_key else None
        self._admin_digest = self._digest(admin_api_key) if admin_api_key else None

    @staticmethod
    def _digest(value: str) -> bytes:
        return hashlib.sha256(value.encode()).digest()

    def authenticate(self, provided: str | None) -> Principal:
        if self._api_key_digest is None and self._admin_digest is None:
            return Principal(name="anonymous", role="admin")
        if not provided:
            raise PermissionDenied("missing API key")
        digest = self._digest(provided)
        if self._admin_digest and hmac.compare_digest(digest, self._admin_digest):
            return Principal(name="admin-key", role="admin")
        if self._api_key_digest and hmac.compare_digest(digest, self._api_key_digest):
            return Principal(name="api-key", role="writer")
        raise PermissionDenied("invalid API key")

    @staticmethod
    def require(principal: Principal, *roles: str) -> None:
        if principal.role not in roles:
            raise PermissionDenied(f"role {principal.role!r} is not allowed")


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: float = 60.0) -> None:
        if limit < 1 or window_seconds <= 0:
            raise ValueError("invalid rate limiter configuration")
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = RLock()

    def check(self, key: str, *, now: float | None = None) -> int:
        timestamp = time.monotonic() if now is None else now
        threshold = timestamp - self.window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= threshold:
                events.popleft()
            if len(events) >= self.limit:
                retry_after = max(1, int(events[0] + self.window_seconds - timestamp + 0.999))
                raise RateLimitExceeded(str(retry_after))
            events.append(timestamp)
            return self.limit - len(events)

# _ci-ref-50723

# _ci-ref-83899

# _ci-ref-48602

# _ci-ref-89346

# _ci-ref-76412

# _ci-ref-62509

# _ci-ref-16202

# _ci-ref-25923

# _ci-ref-72208

# _ci-ref-25003
