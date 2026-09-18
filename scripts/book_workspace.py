#!/usr/bin/env python3
"""Initialize and validate a portable long-PDF reading workspace.

Uses only the Python standard library. It does not parse or modify PDFs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_text_once(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def command_init(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if args.pages < 1:
        raise ValueError("--pages must be a positive integer")

    for relative in (
        "source",
        "pages/text",
        "pages/images",
        "notes/chunks",
        "notes/chapters",
        "assets/equations",
        "assets/tables",
        "assets/figures",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)

    source_path = Path(args.source).expanduser()
    source_hash = ""
    if source_path.is_file():
        source_hash = sha256_file(source_path)

    timestamp = now_iso()
    manifest_path = root / "book_manifest.json"
    if manifest_path.exists():
        raise FileExistsError(
            f"{manifest_path} already exists; choose a new workspace or resume it"
        )

    manifest = {
        "schema_version": "1.0",
        "title": args.title,
        "source_path": str(source_path),
        "source_sha256": source_hash,
        "pdf_pages": args.pages,
        "languages": [item.strip() for item in args.languages.split(",") if item.strip()],
        "document_type": "unknown",
        "created_at": timestamp,
        "updated_at": timestamp,
        "extraction": {
            "text_layer": "unknown",
            "ocr_engine": "",
            "ocr_settings": "",
            "render_settings": "",
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    with (root / "page_map.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["pdf_page", "printed_page", "heading_path", "page_type", "notes"])
        for page in range(1, args.pages + 1):
            writer.writerow([page, "", "", "", ""])

    with (root / "coverage.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "pdf_page",
                "status",
                "chunk_id",
                "ocr_status",
                "visual_status",
                "updated_at",
                "notes",
            ]
        )
        for page in range(1, args.pages + 1):
            writer.writerow([page, "pending", "", "not_run", "not_checked", "", ""])

    write_text_once(
        root / "book_map.md",
        "# Book map\n\n## Identity and coverage\n\n## Pagination map\n\n"
        "## Heading tree\n\n## Global thesis and scope\n\n## Chapter map\n\n"
        "| Chapter | Purpose | Key topics | PDF pages | Note |\n"
        "| --- | --- | --- | --- | --- |\n\n"
        "## Terminology and bilingual aliases\n\n"
        "## Equation / table / figure index\n\n"
        "## Cross-chapter themes and conflicts\n\n"
        "## Known extraction or coverage limitations\n",
    )
    write_text_once(
        root / "evidence_ledger.md",
        "# Evidence ledger\n\n"
        "| Evidence ID | Claim or question | Source pages / chunks | Role | Verification | Notes |\n"
        "| --- | --- | --- | --- | --- | --- |\n",
    )
    write_text_once(
        root / "session_state.md",
        "# Session state\n\n"
        f"- Source identity/hash: {source_hash or 'not recorded'}\n"
        "- Operating mode: index\n"
        "- Actual coverage level: not started\n"
        "- Last completed batch: none\n"
        "- Next PDF page / chunk: 1\n"
        "- Current question:\n"
        "- Active evidence packet:\n"
        "- Low-confidence pages:\n"
        "- Unresolved issues:\n"
        "- Stale derived notes:\n"
        "- Next action: preflight and page mapping\n"
        f"- Updated at: {timestamp}\n",
    )
    write_text_once(
        root / "source" / "README.md",
        "# Source\n\nKeep the original PDF immutable. Record its identity in `book_manifest.json`.\n",
    )

    print(f"Initialized {root} for {args.pages} PDF pages")
    if not source_hash:
        print("Warning: source file was not available; SHA-256 was not recorded")
    return 0


def read_csv_pages(path: Path) -> tuple[list[int], list[str]]:
    pages: list[int] = []
    errors: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if "pdf_page" not in (reader.fieldnames or []):
            return [], [f"{path.name}: missing pdf_page column"]
        for row_number, row in enumerate(reader, start=2):
            try:
                pages.append(int(row["pdf_page"]))
            except (TypeError, ValueError):
                errors.append(f"{path.name}:{row_number}: invalid pdf_page")
    return pages, errors


def command_validate(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    required = [
        "book_manifest.json",
        "page_map.csv",
        "coverage.csv",
        "book_map.md",
        "evidence_ledger.md",
        "session_state.md",
        "notes/chunks",
        "notes/chapters",
    ]
    for relative in required:
        if not (root / relative).exists():
            errors.append(f"missing: {relative}")

    manifest_path = root / "book_manifest.json"
    expected_pages = 0
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            expected_pages = int(manifest.get("pdf_pages", 0))
            if expected_pages < 1:
                errors.append("book_manifest.json: pdf_pages must be positive")
            source = Path(str(manifest.get("source_path", ""))).expanduser()
            recorded_hash = str(manifest.get("source_sha256", ""))
            if source.is_file() and recorded_hash:
                current_hash = sha256_file(source)
                if current_hash != recorded_hash:
                    errors.append("source SHA-256 differs from the manifest")
            elif not recorded_hash:
                warnings.append("source SHA-256 is not recorded")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"book_manifest.json: {exc}")

    for filename in ("page_map.csv", "coverage.csv"):
        path = root / filename
        if not path.is_file():
            continue
        pages, csv_errors = read_csv_pages(path)
        errors.extend(csv_errors)
        seen: set[int] = set()
        duplicates: set[int] = set()
        for page in pages:
            if page in seen:
                duplicates.add(page)
            seen.add(page)
        if duplicates:
            errors.append(f"{filename}: duplicate pages {sorted(duplicates)[:20]}")
        if expected_pages:
            expected = set(range(1, expected_pages + 1))
            actual = set(pages)
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            if missing:
                errors.append(f"{filename}: missing pages {missing[:20]}")
            if extra:
                errors.append(f"{filename}: out-of-range pages {extra[:20]}")

    coverage_path = root / "coverage.csv"
    if coverage_path.is_file():
        allowed_status = {"pending", "excluded", "surveyed", "indexed", "audited"}
        with coverage_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row_number, row in enumerate(rows, start=2):
            status = row.get("status", "")
            if status not in allowed_status:
                errors.append(f"coverage.csv:{row_number}: invalid status {status!r}")
            if status == "excluded" and not row.get("notes", "").strip():
                errors.append(f"coverage.csv:{row_number}: excluded page needs a reason")
            if status in {"indexed", "audited"} and not row.get("chunk_id", "").strip():
                warnings.append(f"coverage.csv:{row_number}: {status} page has no chunk_id")
        pending = sum(1 for row in rows if row.get("status") == "pending")
        if pending:
            warnings.append(f"coverage is incomplete: {pending} page(s) pending")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(f"Validation failed with {len(errors)} error(s)")
        return 1
    print(f"Validation passed with {len(warnings)} warning(s)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize or validate a long-PDF reading workspace"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a new workspace")
    init_parser.add_argument("--root", required=True)
    init_parser.add_argument("--title", required=True)
    init_parser.add_argument("--source", required=True)
    init_parser.add_argument("--pages", required=True, type=int)
    init_parser.add_argument("--languages", default="zh,en")
    init_parser.set_defaults(func=command_init)

    validate_parser = subparsers.add_parser("validate", help="validate a workspace")
    validate_parser.add_argument("--root", required=True)
    validate_parser.set_defaults(func=command_validate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except Exception as exc:  # concise CLI boundary; keep traceback out of agent logs
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
