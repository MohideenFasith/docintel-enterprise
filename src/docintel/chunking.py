from __future__ import annotations

import re
from hashlib import sha1

from .models import Chunk

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def _choose_boundary(text: str, start: int, hard_end: int, min_size: int) -> int:
    if hard_end >= len(text):
        return len(text)
    window = text[start:hard_end]
    candidates: list[int] = []
    for marker in ("\n\n", "\n", ". ", "? ", "! ", "; "):
        pos = window.rfind(marker)
        if pos >= min_size:
            candidates.append(start + pos + len(marker))
    return max(candidates) if candidates else hard_end


def chunk_text(
    document_id: str,
    text: str,
    *,
    max_chars: int = 1_200,
    overlap: int = 120,
    min_chunk_chars: int = 200,
) -> list[Chunk]:
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= max_chars:
        raise ValueError("max_chars must be greater than overlap")
    if min_chunk_chars < 1 or min_chunk_chars > max_chars:
        raise ValueError("min_chunk_chars must be between 1 and max_chars")
    if not text:
        return []

    chunks: list[Chunk] = []
    start = 0
    ordinal = 0
    while start < len(text):
        hard_end = min(len(text), start + max_chars)
        end = _choose_boundary(text, start, hard_end, min_chunk_chars)
        if end <= start:
            end = hard_end
        raw = text[start:end]
        trimmed = raw.strip()
        if trimmed:
            left_trim = len(raw) - len(raw.lstrip())
            right_trim = len(raw) - len(raw.rstrip())
            actual_start = start + left_trim
            actual_end = end - right_trim
            digest = sha1(f"{document_id}:{ordinal}:{actual_start}:{actual_end}".encode()).hexdigest()[:16]
            chunks.append(
                Chunk(
                    id=f"chk_{digest}",
                    document_id=document_id,
                    ordinal=ordinal,
                    text=trimmed,
                    start_char=actual_start,
                    end_char=actual_end,
                    token_estimate=estimate_tokens(trimmed),
                )
            )
            ordinal += 1
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_BOUNDARY.split(text.strip()) if part.strip()]

# _ci-ref-96364
