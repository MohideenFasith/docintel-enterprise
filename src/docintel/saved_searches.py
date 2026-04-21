from __future__ import annotations

from threading import RLock
from uuid import uuid4

from .models import SavedSearch, SavedSearchIn, utcnow


class SavedSearchNotFound(KeyError):
    pass


class SavedSearchStore:
    def __init__(self) -> None:
        self._items: dict[str, SavedSearch] = {}
        self._lock = RLock()

    def create(self, payload: SavedSearchIn, *, owner: str) -> SavedSearch:
        record = SavedSearch(id=f"search_{uuid4().hex}", owner=owner, **payload.model_dump())
        with self._lock:
            self._items[record.id] = record.model_copy(deep=True)
        return record.model_copy(deep=True)

    def get(self, search_id: str, *, owner: str | None = None) -> SavedSearch:
        with self._lock:
            record = self._items.get(search_id)
            if record is None or (owner is not None and record.owner != owner):
                raise SavedSearchNotFound(search_id)
            return record.model_copy(deep=True)

    def list(self, *, owner: str | None = None) -> list[SavedSearch]:
        with self._lock:
            values = list(self._items.values())
        if owner is not None:
            values = [item for item in values if item.owner == owner]
        return [item.model_copy(deep=True) for item in sorted(values, key=lambda item: (item.name.lower(), item.id))]

    def replace(self, search_id: str, payload: SavedSearchIn, *, owner: str) -> SavedSearch:
        current = self.get(search_id, owner=owner)
        updated = current.model_copy(update={**payload.model_dump(), "updated_at": utcnow()})
        with self._lock:
            self._items[search_id] = updated.model_copy(deep=True)
        return updated.model_copy(deep=True)

    def delete(self, search_id: str, *, owner: str) -> None:
        self.get(search_id, owner=owner)
        with self._lock:
            del self._items[search_id]

# _ci-ref-59197

# _ci-ref-38818

# _ci-ref-14268

# _ci-ref-83071

# _ci-ref-12900

# _ci-ref-38039

# _ci-ref-54572

# _ci-ref-70570

# _ci-ref-86027

# _ci-ref-39372

# _ci-ref-53842

# _ci-ref-47214

# _ci-ref-78019

# _ci-ref-92154

# _ci-ref-17087

# _ci-ref-68619

# _ci-ref-24416

# _ci-ref-91134

# _ci-ref-72118

# _ci-ref-31771

# _ci-ref-51048

# _ci-ref-36151

# _ci-ref-19432

# _ci-ref-53374

# _ci-ref-48362

# _ci-ref-71585

# _ci-ref-34400

# _ci-ref-57823

# _ci-ref-27261

# _ci-ref-80481

# _ci-ref-42639

# _ci-ref-83396

# _ci-ref-20874

# _ci-ref-17752

# _ci-ref-16872

# _ci-ref-30946

# _ci-ref-18146

# _ci-ref-93020

# _ci-ref-90779
