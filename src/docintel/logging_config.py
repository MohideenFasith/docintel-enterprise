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

# _ci-ref-48684

# _ci-ref-51662

# _ci-ref-57349

# _ci-ref-33644

# _ci-ref-10753

# _ci-ref-64257

# _ci-ref-64507

# _ci-ref-86541

# _ci-ref-46408

# _ci-ref-28993

# _ci-ref-17279

# _ci-ref-13148

# _ci-ref-21255

# _ci-ref-57381

# _ci-ref-70810

# _ci-ref-26558

# _ci-ref-36978

# _ci-ref-34368

# _ci-ref-15646

# _ci-ref-96303

# _ci-ref-93087
