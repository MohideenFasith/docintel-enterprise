from __future__ import annotations

import logging
from datetime import datetime, timezone

from pythonjsonlogger import json


class DocIntelJsonFormatter(json.JsonFormatter):
    """Structured formatter with stable field names for log processors."""

    def add_fields(self, log_record: dict[str, object], record: logging.LogRecord, message_dict: dict[str, object]) -> None:
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(
        DocIntelJsonFormatter(
            "%(timestamp)s %(level)s %(logger)s %(message)s %(request_id)s %(actor)s",
            rename_fields={"message": "event"},
            static_fields={"service": "docintel-enterprise"},
            defaults={"request_id": None, "actor": None},
        )
    )
    root.addHandler(handler)
    root.setLevel(level.upper())
