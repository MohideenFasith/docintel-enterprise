from __future__ import annotations

from threading import RLock

from .models import DocumentIn, ExtractedMetadata, IngestionPolicy, PolicyDecision


class PolicyNotFound(KeyError):
    pass


class IngestionPolicyEngine:
    """Deterministic pre-ingestion policy evaluation.

    Policies are ordered by priority/name. Matching rules may reject a document
    or add normalized tags. The engine never mutates the caller's payload.
    """

    def __init__(self) -> None:
        self._policies: dict[str, IngestionPolicy] = {}
        self._lock = RLock()

    def upsert(self, policy: IngestionPolicy) -> IngestionPolicy:
        stored = policy.model_copy(deep=True)
        with self._lock:
            self._policies[stored.name] = stored
        return stored.model_copy(deep=True)

    def get(self, name: str) -> IngestionPolicy:
        with self._lock:
            policy = self._policies.get(name)
            if policy is None:
                raise PolicyNotFound(name)
            return policy.model_copy(deep=True)

    def list(self) -> list[IngestionPolicy]:
        with self._lock:
            values = list(self._policies.values())
        values.sort(key=lambda policy: (policy.priority, policy.name.lower()))
        return [policy.model_copy(deep=True) for policy in values]

    def delete(self, name: str) -> None:
        self.get(name)
        with self._lock:
            del self._policies[name]

    @staticmethod
    def _matches(policy: IngestionPolicy, payload: DocumentIn) -> bool:
        if not policy.enabled:
            return False
        if policy.source_equals is not None and payload.source != policy.source_equals:
            return False
        if policy.require_any_tags and not set(policy.require_any_tags).intersection(payload.tags):
            return False
        return True

    def evaluate(self, payload: DocumentIn, extracted: ExtractedMetadata) -> PolicyDecision:
        content_lower = payload.content.lower()
        matched: list[str] = []
        violations: list[str] = []
        added: set[str] = set()

        for policy in self.list():
            if not self._matches(policy, payload):
                continue
            matched.append(policy.name)
            for phrase in policy.block_phrases:
                if phrase in content_lower:
                    violations.append(f"{policy.name}: blocked phrase {phrase!r}")
            if policy.max_emails is not None and len(extracted.emails) > policy.max_emails:
                violations.append(
                    f"{policy.name}: email count {len(extracted.emails)} exceeds {policy.max_emails}"
                )
            if policy.max_urls is not None and len(extracted.urls) > policy.max_urls:
                violations.append(f"{policy.name}: url count {len(extracted.urls)} exceeds {policy.max_urls}")
            added.update(policy.add_tags)

        return PolicyDecision(
            accepted=not violations,
            matched_policies=matched,
            violations=violations,
            add_tags=sorted(added),
        )

# _ci-ref-30889

# _ci-ref-23911

# _ci-ref-94341

# _ci-ref-15136

# _ci-ref-66224

# _ci-ref-96362

# _ci-ref-43902

# _ci-ref-24833

# _ci-ref-60343

# _ci-ref-14337

# _ci-ref-22541

# _ci-ref-26083

# _ci-ref-94498

# _ci-ref-97475

# _ci-ref-30093

# _ci-ref-83328

# _ci-ref-86939

# _ci-ref-84959

# _ci-ref-50180

# _ci-ref-30380

# _ci-ref-49257

# _ci-ref-68171

# _ci-ref-67712

# _ci-ref-20151

# _ci-ref-38074

# _ci-ref-86980

# _ci-ref-63641

# _ci-ref-58390

# _ci-ref-73344

# _ci-ref-71849

# _ci-ref-17901

# _ci-ref-66675

# _ci-ref-57167

# _ci-ref-36989
