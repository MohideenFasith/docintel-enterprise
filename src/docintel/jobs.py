from __future__ import annotations

from collections import deque
from threading import RLock
from typing import Callable
from uuid import uuid4

from .models import JobRecord, JobStatus, utcnow


class JobQueue:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._pending: deque[str] = deque()
        self._handlers: dict[str, Callable[[dict], None]] = {}
        self._lock = RLock()

    def register(self, kind: str, handler: Callable[[dict], None]) -> None:
        self._handlers[kind] = handler

    def enqueue(self, kind: str, payload: dict) -> JobRecord:
        job = JobRecord(id=f"job_{uuid4().hex}", kind=kind, payload=payload)
        with self._lock:
            self._jobs[job.id] = job
            self._pending.append(job.id)
        return job.model_copy(deep=True)

    def get(self, job_id: str) -> JobRecord:
        with self._lock:
            return self._jobs[job_id].model_copy(deep=True)

    def run_next(self) -> JobRecord | None:
        with self._lock:
            if not self._pending:
                return None
            job_id = self._pending.popleft()
            job = self._jobs[job_id]
            job.status = JobStatus.RUNNING
            job.attempts += 1
            job.updated_at = utcnow()
        handler = self._handlers.get(job.kind)
        try:
            if handler is None:
                raise RuntimeError(f"no handler registered for {job.kind}")
            handler(job.payload)
        except Exception as exc:
            with self._lock:
                job.status = JobStatus.FAILED
                job.error = str(exc)
                job.updated_at = utcnow()
            return job.model_copy(deep=True)
        with self._lock:
            job.status = JobStatus.SUCCEEDED
            job.updated_at = utcnow()
        return job.model_copy(deep=True)

    def pending_count(self) -> int:
        with self._lock:
            return len(self._pending)

# _ci-ref-62727

# _ci-ref-85582

# _ci-ref-89076

# _ci-ref-42534

# _ci-ref-82628

# _ci-ref-17686

# _ci-ref-95208

# _ci-ref-25509

# _ci-ref-97590

# _ci-ref-88134

# _ci-ref-53231

# _ci-ref-61131

# _ci-ref-87251

# _ci-ref-95089

# _ci-ref-32119

# _ci-ref-64396
