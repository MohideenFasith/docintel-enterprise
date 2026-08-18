from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class RedactionKind(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    IPV4 = "ipv4"
    API_KEY = "api_key"


_PATTERNS: dict[RedactionKind, re.Pattern[str]] = {
    RedactionKind.EMAIL: re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    RedactionKind.PHONE: re.compile(r"(?<!\w)(?:\+?\d[\d .()-]{7,}\d)(?!\w)"),
    RedactionKind.CREDIT_CARD: re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)"),
    RedactionKind.IPV4: re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    RedactionKind.API_KEY: re.compile(r"\b(?:sk|api|key)[_-][A-Za-z0-9_-]{12,}\b", re.IGNORECASE),
}


@dataclass(slots=True)
class Redaction:
    kind: RedactionKind
    start: int
    end: int
    original: str
    replacement: str


@dataclass(slots=True)
class RedactionResult:
    text: str
    redactions: list[Redaction] = field(default_factory=list)


class Redactor:
    def __init__(self, enabled: set[RedactionKind] | None = None) -> None:
        self.enabled = enabled or set(RedactionKind)

    @staticmethod
    def _valid_luhn(value: str) -> bool:
        digits = [int(char) for char in value if char.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        checksum = 0
        parity = len(digits) % 2
        for index, digit in enumerate(digits):
            if index % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        return checksum % 10 == 0

    @staticmethod
    def _valid_ipv4(value: str) -> bool:
        try:
            return all(0 <= int(part) <= 255 for part in value.split("."))
        except ValueError:
            return False

    def scan(self, text: str) -> list[Redaction]:
        candidates: list[Redaction] = []
        for kind in sorted(self.enabled, key=lambda item: item.value):
            pattern = _PATTERNS[kind]
            for match in pattern.finditer(text):
                original = match.group(0)
                if kind == RedactionKind.CREDIT_CARD and not self._valid_luhn(original):
                    continue
                if kind == RedactionKind.IPV4 and not self._valid_ipv4(original):
                    continue
                candidates.append(
                    Redaction(
                        kind=kind,
                        start=match.start(),
                        end=match.end(),
                        original=original,
                        replacement=f"[REDACTED_{kind.value.upper()}]",
                    )
                )
        candidates.sort(key=lambda item: (item.start, -(item.end - item.start)))
        output: list[Redaction] = []
        end = -1
        for candidate in candidates:
            if candidate.start >= end:
                output.append(candidate)
                end = candidate.end
        return output

    def redact(self, text: str) -> RedactionResult:
        matches = self.scan(text)
        if not matches:
            return RedactionResult(text=text)
        parts: list[str] = []
        cursor = 0
        for match in matches:
            parts.append(text[cursor : match.start])
            parts.append(match.replacement)
            cursor = match.end
        parts.append(text[cursor:])
        return RedactionResult(text="".join(parts), redactions=matches)
