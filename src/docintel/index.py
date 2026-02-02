from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from threading import RLock

from .models import Chunk, DocumentRecord, SearchHit

_TOKEN = re.compile(r"[a-z0-9][a-z0-9_-]{1,}", re.IGNORECASE)
_STOPWORDS = {
    "the", "and", "for", "that", "with", "from", "this", "are", "was", "were", "have", "has",
    "into", "your", "you", "its", "our", "but", "not", "can", "will", "their", "they", "them",
}


def tokenize(text: str) -> list[str]:
    return [token for token in (match.group(0).lower() for match in _TOKEN.finditer(text)) if token not in _STOPWORDS]


@dataclass(slots=True)
class _IndexedChunk:
    document: DocumentRecord
    chunk: Chunk
    term_counts: Counter[str]
    length: int


class LexicalIndex:
    """Small BM25-like inverted index with document metadata filtering."""

    def __init__(self, *, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._chunks: dict[str, _IndexedChunk] = {}
        self._postings: dict[str, set[str]] = defaultdict(set)
        self._document_chunks: dict[str, set[str]] = defaultdict(set)
        self._lock = RLock()

    def index_document(self, document: DocumentRecord, chunks: list[Chunk]) -> None:
        with self._lock:
            self.remove_document(document.id)
            for chunk in chunks:
                terms = tokenize(f"{document.title} {chunk.text} {' '.join(document.tags)}")
                entry = _IndexedChunk(document=document, chunk=chunk, term_counts=Counter(terms), length=max(1, len(terms)))
                self._chunks[chunk.id] = entry
                self._document_chunks[document.id].add(chunk.id)
                for term in entry.term_counts:
                    self._postings[term].add(chunk.id)

    def remove_document(self, document_id: str) -> None:
        with self._lock:
            chunk_ids = self._document_chunks.pop(document_id, set())
            for chunk_id in chunk_ids:
                entry = self._chunks.pop(chunk_id, None)
                if entry is None:
                    continue
                for term in entry.term_counts:
                    posting = self._postings.get(term)
                    if posting is not None:
                        posting.discard(chunk_id)
                        if not posting:
                            self._postings.pop(term, None)

    def _avg_length(self) -> float:
        if not self._chunks:
            return 1.0
        return sum(entry.length for entry in self._chunks.values()) / len(self._chunks)

    def _score_term(self, term: str, entry: _IndexedChunk, avg_length: float) -> float:
        tf = entry.term_counts.get(term, 0)
        if not tf:
            return 0.0
        n = len(self._chunks)
        df = len(self._postings.get(term, ()))
        idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
        denominator = tf + self.k1 * (1 - self.b + self.b * entry.length / avg_length)
        return idf * (tf * (self.k1 + 1)) / denominator

    def search(
        self,
        query: str,
        *,
        limit: int = 10,
        required_tag: str | None = None,
        source: str | None = None,
    ) -> list[SearchHit]:
        terms = list(dict.fromkeys(tokenize(query)))
        if not terms:
            return []
        with self._lock:
            candidate_ids: set[str] = set()
            for term in terms:
                candidate_ids.update(self._postings.get(term, set()))
            avg_length = self._avg_length()
            hits: list[SearchHit] = []
            for chunk_id in candidate_ids:
                entry = self._chunks[chunk_id]
                if required_tag and required_tag not in entry.document.tags:
                    continue
                if source and source != entry.document.source:
                    continue
                matched_terms = [term for term in terms if term in entry.term_counts]
                score = sum(self._score_term(term, entry, avg_length) for term in matched_terms)
                title_terms = set(tokenize(entry.document.title))
                score += 0.35 * len(title_terms.intersection(terms))
                if score <= 0:
                    continue
                hits.append(
                    SearchHit(
                        document_id=entry.document.id,
                        chunk_id=entry.chunk.id,
                        title=entry.document.title,
                        snippet=self._snippet(entry.chunk.text, matched_terms),
                        score=round(score, 6),
                        matched_terms=matched_terms,
                        tags=entry.document.tags,
                    )
                )
            hits.sort(key=lambda hit: (-hit.score, hit.document_id, hit.chunk_id))
            return hits[:limit]

    @staticmethod
    def _snippet(text: str, terms: list[str], radius: int = 120) -> str:
        lowered = text.lower()
        positions = [lowered.find(term.lower()) for term in terms]
        positions = [position for position in positions if position >= 0]
        if not positions:
            return text[: radius * 2]
        position = min(positions)
        start = max(0, position - radius)
        end = min(len(text), position + radius)
        snippet = text[start:end].strip()
        if start:
            snippet = "…" + snippet
        if end < len(text):
            snippet += "…"
        return snippet

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "chunks": len(self._chunks),
                "terms": len(self._postings),
                "documents": len(self._document_chunks),
            }

# _ci-ref-67261

# _ci-ref-68428

# _ci-ref-15164

# _ci-ref-77350

# _ci-ref-63363

# _ci-ref-31146

# _ci-ref-43205

# _ci-ref-67496

# _ci-ref-93623

# _ci-ref-94957

# _ci-ref-80165

# _ci-ref-43612

# _ci-ref-44116

# _ci-ref-71228

# _ci-ref-36146

# _ci-ref-64154

# _ci-ref-59034

# _ci-ref-43130

# _ci-ref-21510

# _ci-ref-80310

# _ci-ref-70390

# _ci-ref-40792

# _ci-ref-59005

# _ci-ref-62194

# _ci-ref-98894

# _ci-ref-77970
