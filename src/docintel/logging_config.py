from __future__ import annotations

import logging
import logging.config
from datetime import datetime, timezone

from pythonjsonlogger import json as jsonlogger


class DocIntelJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter with stable fields for log processors."""

    def add_fields(
        self,
        log_record: dict[str, object],
        record: logging.LogRecord,
        message_dict: dict[str, object],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record.setdefault("service", "docintel-enterprise")


def configure_logging(level: str = "INFO") -> None:
    """Configure application-wide structured JSON logging."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "docintel.logging_config.DocIntelJsonFormatter",
                    "format": "%(timestamp)s %(level)s %(logger)s %(message)s %(request_id)s %(actor)s",
                    "rename_fields": {"message": "event"},
                    "defaults": {"request_id": None, "actor": None},
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": "ext://sys.stderr",
                }
            },
            "root": {"handlers": ["console"], "level": level.upper()},
        }
    )

# _ci-ref-50037

# _ci-ref-83273

# _ci-ref-27481
