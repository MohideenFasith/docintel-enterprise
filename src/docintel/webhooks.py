from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import RLock
from uuid import uuid4


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class WebhookEndpoint:
    id: str
    url: str
    secret: str
    events: set[str]
    enabled: bool = True


@dataclass(slots=True)
class Delivery:
    id: str
    endpoint_id: str
    event: str
    payload: dict
    attempt: int = 0
    next_attempt_at: datetime = field(default_factory=_now)
    delivered_at: datetime | None = None
    last_error: str | None = None


class WebhookRegistry:
    def __init__(self) -> None:
        self._endpoints: dict[str, WebhookEndpoint] = {}
        self._deliveries: dict[str, Delivery] = {}
        self._lock = RLock()

    def register(self, url: str, secret: str, events: set[str]) -> WebhookEndpoint:
        if not url.startswith(("https://", "http://localhost", "http://127.0.0.1")):
            raise ValueError("webhook URL must use HTTPS outside localhost")
        if len(secret) < 16:
            raise ValueError("webhook secret must be at least 16 characters")
        endpoint = WebhookEndpoint(id=f"wh_{uuid4().hex}", url=url, secret=secret, events=set(events))
        with self._lock:
            self._endpoints[endpoint.id] = endpoint
        return endpoint

    def matching(self, event: str) -> list[WebhookEndpoint]:
        with self._lock:
            return [endpoint for endpoint in self._endpoints.values() if endpoint.enabled and event in endpoint.events]

    def enqueue(self, event: str, payload: dict) -> list[Delivery]:
        deliveries: list[Delivery] = []
        with self._lock:
            for endpoint in self.matching(event):
                delivery = Delivery(id=f"del_{uuid4().hex}", endpoint_id=endpoint.id, event=event, payload=payload.copy())
                self._deliveries[delivery.id] = delivery
                deliveries.append(delivery)
        return deliveries

    def sign(self, endpoint_id: str, payload: dict) -> str:
        with self._lock:
            endpoint = self._endpoints[endpoint_id]
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        digest = hmac.new(endpoint.secret.encode(), body, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def due(self, now: datetime | None = None) -> list[Delivery]:
        timestamp = now or _now()
        with self._lock:
            return [
                delivery
                for delivery in self._deliveries.values()
                if delivery.delivered_at is None and delivery.next_attempt_at <= timestamp
            ]

    def mark_success(self, delivery_id: str) -> Delivery:
        with self._lock:
            delivery = self._deliveries[delivery_id]
            delivery.attempt += 1
            delivery.delivered_at = _now()
            delivery.last_error = None
            return delivery

    def mark_failure(self, delivery_id: str, error: str) -> Delivery:
        with self._lock:
            delivery = self._deliveries[delivery_id]
            delivery.attempt += 1
            delivery.last_error = error[:500]
            delay_seconds = min(3_600, 2 ** min(delivery.attempt, 10))
            delivery.next_attempt_at = _now() + timedelta(seconds=delay_seconds)
            return delivery
