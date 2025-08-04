from __future__ import annotations

from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True, slots=True)
class TenantQuota:
    max_documents: int = 10_000
    max_total_chars: int = 100_000_000


@dataclass(frozen=True, slots=True)
class TenantUsage:
    documents: int = 0
    total_chars: int = 0


class QuotaExceeded(ValueError):
    pass


class TenantQuotaManager:
    def __init__(self) -> None:
        self._quotas: dict[str, TenantQuota] = {}
        self._usage: dict[str, TenantUsage] = {}
        self._lock = RLock()

    def configure(self, tenant_id: str, quota: TenantQuota) -> None:
        if quota.max_documents < 1 or quota.max_total_chars < 1:
            raise ValueError("quota limits must be positive")
        with self._lock:
            self._quotas[tenant_id] = quota
            self._usage.setdefault(tenant_id, TenantUsage())

    def quota(self, tenant_id: str) -> TenantQuota:
        with self._lock:
            return self._quotas.get(tenant_id, TenantQuota())

    def usage(self, tenant_id: str) -> TenantUsage:
        with self._lock:
            return self._usage.get(tenant_id, TenantUsage())

    def reserve_document(self, tenant_id: str, chars: int) -> TenantUsage:
        if chars < 0:
            raise ValueError("chars must be non-negative")
        with self._lock:
            quota = self._quotas.get(tenant_id, TenantQuota())
            usage = self._usage.get(tenant_id, TenantUsage())
            next_usage = TenantUsage(usage.documents + 1, usage.total_chars + chars)
            if next_usage.documents > quota.max_documents:
                raise QuotaExceeded("document count quota exceeded")
            if next_usage.total_chars > quota.max_total_chars:
                raise QuotaExceeded("character quota exceeded")
            self._usage[tenant_id] = next_usage
            return next_usage

    def release_document(self, tenant_id: str, chars: int) -> TenantUsage:
        with self._lock:
            usage = self._usage.get(tenant_id, TenantUsage())
            next_usage = TenantUsage(max(0, usage.documents - 1), max(0, usage.total_chars - max(chars, 0)))
            self._usage[tenant_id] = next_usage
            return next_usage

# _ci-ref-98358

# _ci-ref-66774

# _ci-ref-40508

# _ci-ref-97690

# _ci-ref-98918

# _ci-ref-36255

# _ci-ref-29605

# _ci-ref-30715

# _ci-ref-91689

# _ci-ref-50913

# _ci-ref-49834

# _ci-ref-22809

# _ci-ref-52936

# _ci-ref-61345

# _ci-ref-15896

# _ci-ref-67127

# _ci-ref-26822

# _ci-ref-68755

# _ci-ref-17525

# _ci-ref-17968
