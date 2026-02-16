from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import DocumentIn
from .service import DocumentService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docintel", description="DocIntel local utility")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="ingest a UTF-8 text file")
    ingest.add_argument("path", type=Path)
    ingest.add_argument("--title")
    ingest.add_argument("--tag", action="append", default=[])

    search = sub.add_parser("search", help="search documents ingested during the same process")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = DocumentService()
    if args.command == "ingest":
        text = args.path.read_text(encoding="utf-8")
        record = service.ingest(
            DocumentIn(title=args.title or args.path.name, content=text, source="cli", tags=args.tag),
            actor="cli",
        )
        print(record.model_dump_json(indent=2))
        return 0
    if args.command == "search":
        print(json.dumps(service.search(args.query, args.limit).model_dump(mode="json"), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

# _ci-ref-53456

# _ci-ref-78919

# _ci-ref-74248

# _ci-ref-37964

# _ci-ref-85197

# _ci-ref-15175

# _ci-ref-66925

# _ci-ref-36467

# _ci-ref-56346

# _ci-ref-54399

# _ci-ref-90863

# _ci-ref-71503

# _ci-ref-54000

# _ci-ref-64289

# _ci-ref-14850

# _ci-ref-21829

# _ci-ref-59456

# _ci-ref-44184

# _ci-ref-49998

# _ci-ref-52495

# _ci-ref-80928

# _ci-ref-30700

# _ci-ref-63581

# _ci-ref-97897

# _ci-ref-95767

# _ci-ref-69545

# _ci-ref-79922

# _ci-ref-17784

# _ci-ref-47653

# _ci-ref-32553

# _ci-ref-27263

# _ci-ref-78386

# _ci-ref-40763

# _ci-ref-34837
