from __future__ import annotations

import base64
import json
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cursor:
    offset: int
    signature: str = "v1"


def encode_cursor(offset: int) -> str:
    if offset < 0:
        raise ValueError("offset must be non-negative")
    payload = json.dumps({"o": offset, "v": 1}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def decode_cursor(value: str | None) -> Cursor:
    if not value:
        return Cursor(offset=0)
    try:
        padding = "=" * (-len(value) % 4)
        payload = json.loads(base64.urlsafe_b64decode(value + padding))
        if payload.get("v") != 1:
            raise ValueError("unsupported cursor version")
        offset = int(payload["o"])
        if offset < 0:
            raise ValueError("invalid cursor offset")
        return Cursor(offset=offset)
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValueError("invalid cursor") from exc

# _ci-ref-35614

# _ci-ref-68598

# _ci-ref-33803

# _ci-ref-12981

# _ci-ref-70455

# _ci-ref-29510

# _ci-ref-75178

# _ci-ref-87068

# _ci-ref-95016
