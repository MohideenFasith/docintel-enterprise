from __future__ import annotations

import difflib
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock

from .models import DocumentRecord


@dataclass(frozen=True, slots=True)
class DocumentVersion:
    document_id: str
    version: int
    title: str
    content: str
    tags: tuple[str, ...]
    captured_at: datetime


class VersionStore:
    def __init__(self, max_versions_per_document: int = 100) -> None:
        if max_versions_per_document < 1:
            raise ValueError("max_versions_per_document must be positive")
        self.max_versions = max_versions_per_document
        self._versions: dict[str, list[DocumentVersion]] = {}
        self._lock = RLock()

    def capture(self, record: DocumentRecord) -> DocumentVersion:
        version = DocumentVersion(
            document_id=record.id,
            version=record.version,
            title=record.title,
            content=record.content,
            tags=tuple(record.tags),
            captured_at=datetime.now(timezone.utc),
        )
        with self._lock:
            versions = self._versions.setdefault(record.id, [])
            if versions and versions[-1].version == version.version:
                versions[-1] = version
            else:
                versions.append(version)
            if len(versions) > self.max_versions:
                del versions[: len(versions) - self.max_versions]
        return version

    def list(self, document_id: str) -> list[DocumentVersion]:
        with self._lock:
            return list(self._versions.get(document_id, []))

    def get(self, document_id: str, version: int) -> DocumentVersion:
        for item in self.list(document_id):
            if item.version == version:
                return item
        raise KeyError((document_id, version))

    def diff(self, document_id: str, from_version: int, to_version: int) -> str:
        before = self.get(document_id, from_version)
        after = self.get(document_id, to_version)
        return "".join(
            difflib.unified_diff(
                before.content.splitlines(keepends=True),
                after.content.splitlines(keepends=True),
                fromfile=f"v{from_version}",
                tofile=f"v{to_version}",
            )
        )

# _ci-ref-91156

# _ci-ref-73273

# _ci-ref-89450

# _ci-ref-68066

# _ci-ref-25315

# _ci-ref-83351

# _ci-ref-41941

# _ci-ref-94323

# _ci-ref-81098

# _ci-ref-81791

# _ci-ref-97097

# _ci-ref-42884

# _ci-ref-91207

# _ci-ref-26108

# _ci-ref-47144

# _ci-ref-65314

# _ci-ref-73998

# _ci-ref-34621

# _ci-ref-11438

# _ci-ref-88642

# _ci-ref-97994

# _ci-ref-90052

# _ci-ref-78692

# _ci-ref-93599

# _ci-ref-47726

# _ci-ref-46553

# _ci-ref-64645

# _ci-ref-56974

# _ci-ref-78839

# _ci-ref-97612

# _ci-ref-80547

# _ci-ref-39454

# _ci-ref-73068

# _ci-ref-31613

# _ci-ref-97409

# _ci-ref-55323

# _ci-ref-76303

# _ci-ref-21584

# _ci-ref-38887
