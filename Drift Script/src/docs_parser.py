"""Documentation parsing utilities for Markdown and MDX files."""

from __future__ import annotations

import re
from pathlib import Path

from .utils import EndpointRecord, allowed_http_methods, normalize_method, normalize_path

HTTP_METHOD_PATTERN = r"(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)"
PATH_PATTERN = r"((?:https?://[^\s`\"')>]+)?/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%{}<>-]*)"
ENDPOINT_PATTERN = re.compile(
    rf"(?P<method>{HTTP_METHOD_PATTERN})\s+(?P<path>{PATH_PATTERN})",
    re.IGNORECASE,
)


def parse_docs_directory(docs_path: str | Path) -> tuple[list[EndpointRecord], list[str]]:
    """Scan a docs directory recursively and return extracted endpoint records."""
    root = Path(docs_path)
    if not root.exists():
        return [], [f"Docs path does not exist: {root}"]
    if not root.is_dir():
        return [], [f"Docs path is not a directory: {root}"]

    records: list[EndpointRecord] = []
    errors: list[str] = []

    for file_path in sorted(root.rglob("*")):
        if file_path.suffix.lower() not in {".md", ".mdx"}:
            continue

        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"Failed to read {file_path}: {exc}")
            continue

        records.extend(extract_documented_endpoints(text, file_path, root))

    deduped = {
        (record.method, record.path, record.source_file): record
        for record in records
    }
    return sorted(deduped.values(), key=lambda item: (item.source_file, item.method, item.path)), errors


def extract_documented_endpoints(
    text: str,
    file_path: Path,
    docs_root: Path,
) -> list[EndpointRecord]:
    """Extract endpoint pairs from Markdown or MDX content using heuristics."""
    records: list[EndpointRecord] = []
    source_file = str(file_path.relative_to(docs_root)).replace("\\", "/")

    for match in ENDPOINT_PATTERN.finditer(text):
        method = normalize_method(match.group("method"))
        path = normalize_path(match.group("path"))
        if method not in allowed_http_methods() or not path.startswith("/"):
            continue
        records.append(
            EndpointRecord(
                method=method,
                path=path,
                source_file=source_file,
            )
        )

    return records
