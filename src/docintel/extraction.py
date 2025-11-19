from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import ExtractedMetadata

_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_URL = re.compile(r"https?://[^\s<>()\[\]{}]+", re.IGNORECASE)
_AMOUNT = re.compile(r"(?<!\w)(?:USD|EUR|GBP|INR|\$|€|£|₹)\s?\d[\d,]*(?:\.\d{1,2})?", re.IGNORECASE)
_DATE = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
_PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d .()-]{7,}\d)(?!\w)")


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        value = value.rstrip(".,;:)")
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def extract_metadata(text: str) -> ExtractedMetadata:
    return ExtractedMetadata(
        emails=_unique(_EMAIL.findall(text)),
        urls=_unique(_URL.findall(text)),
        amounts=_unique(_AMOUNT.findall(text)),
        dates=_unique(_DATE.findall(text)),
        phones=_unique(match.group(0) for match in _PHONE.finditer(text)),
        word_count=len(re.findall(r"\b\w+\b", text, re.UNICODE)),
        line_count=0 if not text else text.count("\n") + 1,
    )


def extract_domains(urls: list[str]) -> list[str]:
    domains: list[str] = []
    for url in urls:
        host = urlparse(url).hostname
        if host:
            domains.append(host.lower())
    return _unique(domains)

# _ci-ref-23425

# _ci-ref-50620

# _ci-ref-66948

# _ci-ref-84912

# _ci-ref-41194

# _ci-ref-55938

# _ci-ref-85361

# _ci-ref-29048

# _ci-ref-49833

# _ci-ref-19229

# _ci-ref-24334

# _ci-ref-25278

# _ci-ref-58224

# _ci-ref-42264

# _ci-ref-64558

# _ci-ref-45107

# _ci-ref-57067

# _ci-ref-62328

# _ci-ref-93188

# _ci-ref-90700

# _ci-ref-40827

# _ci-ref-39235

# _ci-ref-45901

# _ci-ref-22224

# _ci-ref-26591

# _ci-ref-79747

# _ci-ref-45477

# _ci-ref-67524

# _ci-ref-39155

# _ci-ref-16840
