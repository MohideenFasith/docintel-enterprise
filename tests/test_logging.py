from __future__ import annotations

import json
import logging
from io import StringIO

from docintel.logging_config import DocIntelJsonFormatter, configure_logging


def test_configure_logging_installs_json_formatter() -> None:
    configure_logging("INFO")
    root = logging.getLogger()
    assert root.handlers
    assert isinstance(root.handlers[0].formatter, DocIntelJsonFormatter)


def test_json_log_contains_correlation_fields() -> None:
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(
        DocIntelJsonFormatter(
            "%(timestamp)s %(level)s %(logger)s %(message)s %(request_id)s %(actor)s",
            rename_fields={"message": "event"},
            defaults={"request_id": None, "actor": None},
        )
    )
    logger = logging.getLogger("docintel.integration")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.INFO)

    logger.info(
        "document_ingested",
        extra={"request_id": "req-42", "actor": "writer", "document_id": "doc-7"},
    )

    payload = json.loads(stream.getvalue())
    assert payload["event"] == "document_ingested"
    assert payload["request_id"] == "req-42"
    assert payload["actor"] == "writer"
    assert payload["document_id"] == "doc-7"
    assert payload["service"] == "docintel-enterprise"

# _ci-ref-27499

# _ci-ref-84537

# _ci-ref-85582

# _ci-ref-47487

# _ci-ref-27727

# _ci-ref-23491

# _ci-ref-62978

# _ci-ref-69037

# _ci-ref-79742

# _ci-ref-84741

# _ci-ref-74512

# _ci-ref-72294

# _ci-ref-65275

# _ci-ref-19120

# _ci-ref-91684

# _ci-ref-99762

# _ci-ref-56152
