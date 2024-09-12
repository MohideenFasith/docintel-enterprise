from __future__ import annotations

from collections import deque
from threading import RLock
from uuid import uuid4

from .models import AuditEvent


class AuditLog:
    def __init__(self, max_events: int = 10_000) -> None:
        if max_events < 1:
            raise ValueError("max_events must be positive")
        self._events: deque[AuditEvent] = deque(maxlen=max_events)
        self._lock = RLock()

    def record(
        self,
        *,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        outcome: str = "success",
        detail: dict | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=f"aud_{uuid4().hex}",
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            detail=detail or {},
        )
        with self._lock:
            self._events.append(event)
        return event

    def list(self, *, limit: int = 100, actor: str | None = None, action: str | None = None) -> list[AuditEvent]:
        with self._lock:
            events = list(self._events)
        events.reverse()
        if actor:
            events = [event for event in events if event.actor == actor]
        if action:
            events = [event for event in events if event.action == action]
        return events[:limit]

# _ci-ref-77603

# _ci-ref-12612
