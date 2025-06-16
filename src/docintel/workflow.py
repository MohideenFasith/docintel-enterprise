from __future__ import annotations

from threading import RLock

from .errors import WorkflowNotFound
from .models import DocumentRecord, WorkflowDecision, WorkflowRule


class WorkflowRouter:
    def __init__(self) -> None:
        self._rules: dict[str, WorkflowRule] = {}
        self._lock = RLock()

    def upsert(self, rule: WorkflowRule) -> WorkflowRule:
        normalized = rule.model_copy(
            update={
                "any_tags": [tag.strip().lower() for tag in rule.any_tags if tag.strip()],
                "title_contains": [term.strip().lower() for term in rule.title_contains if term.strip()],
            }
        )
        with self._lock:
            self._rules[normalized.name] = normalized
        return normalized

    def delete(self, name: str) -> None:
        with self._lock:
            if name not in self._rules:
                raise WorkflowNotFound(name)
            del self._rules[name]

    def list(self) -> list[WorkflowRule]:
        with self._lock:
            return sorted(self._rules.values(), key=lambda rule: (rule.priority, rule.name))

    def route(self, document: DocumentRecord) -> WorkflowDecision:
        for rule in self.list():
            if not rule.enabled:
                continue
            if self._matches(rule, document):
                return WorkflowDecision(
                    queue=rule.target_queue,
                    rule=rule.name,
                    reason=f"matched workflow rule {rule.name}",
                )
        return WorkflowDecision(queue="general", reason="no workflow rule matched")

    @staticmethod
    def _matches(rule: WorkflowRule, document: DocumentRecord) -> bool:
        if rule.source_equals is not None and document.source != rule.source_equals:
            return False
        if rule.any_tags and not set(rule.any_tags).intersection(document.tags):
            return False
        lowered_title = document.title.lower()
        if rule.title_contains and not any(term in lowered_title for term in rule.title_contains):
            return False
        return True

# _ci-ref-75598

# _ci-ref-32099

# _ci-ref-44471

# _ci-ref-78512

# _ci-ref-51405

# _ci-ref-59732

# _ci-ref-18973

# _ci-ref-20118

# _ci-ref-18668

# _ci-ref-10463

# _ci-ref-87459

# _ci-ref-28208

# _ci-ref-33149

# _ci-ref-92317

# _ci-ref-24131

# _ci-ref-35106

# _ci-ref-88654

# _ci-ref-74175

# _ci-ref-24668

# _ci-ref-57400

# _ci-ref-41407

# _ci-ref-18965

# _ci-ref-92750

# _ci-ref-49986

# _ci-ref-53746

# _ci-ref-14514
