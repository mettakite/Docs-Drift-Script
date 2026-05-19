"""Report rendering and file output helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .utils import ensure_directory


def write_markdown_report(report: dict[str, Any], output_dir: Path) -> Path:
    """Write the markdown drift report to disk."""
    ensure_directory(output_dir)
    output_path = output_dir / "drift_report.md"
    output_path.write_text(render_markdown_report(report), encoding="utf-8")
    return output_path


def write_json_report(report: dict[str, Any], output_dir: Path) -> Path:
    """Write the JSON drift report to disk."""
    ensure_directory(output_dir)
    output_path = output_dir / "drift_report.json"
    output_path.write_text(json.dumps(report, indent=2, sort_keys=False), encoding="utf-8")
    return output_path


def render_markdown_report(report: dict[str, Any]) -> str:
    """Render a human-readable markdown report."""
    summary = report["summary"]
    lines: list[str] = [
        "# API Documentation Drift Report",
        "",
        "## Overview",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Services configured: {summary['services_configured']}",
        f"- Services audited: {summary['services_audited']}",
        f"- Spec fetch complete: {'yes' if summary['spec_fetch_complete'] else 'no'}",
        "",
        "## Audit Summary",
        "",
        "The audit compares endpoint references found in documentation against endpoints defined in the OpenAPI specification(s).",
        "",
        f"- Number of endpoints cited in documentation: {summary['documented_endpoint_count']}",
        f"- Number of endpoints defined in OpenAPI specification(s): {summary['spec_endpoint_count']}",
        f"- Endpoints matched between documentation and specification(s): {summary['matched_endpoint_count']}",
        f"- Undocumented endpoints: {summary['undocumented_endpoint_count']}",
        f"- Documented but missing endpoints: {summary['documented_missing_endpoint_count']}",
        f"- Documentation parsing errors: {summary['docs_errors_count']}",
        "",
        "## Coverage By Service",
        "",
        "| Service | Spec URL | Spec Endpoints | Matched | Undocumented | Coverage |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]

    for service in report["services"]:
        lines.append(
            "| {service} | {spec_url} | {spec_endpoint_count} | {matched_count} | "
            "{undocumented_count} | {coverage_percentage}% |".format(**service)
        )

    lines.extend(["", "## Undocumented Endpoints", ""])
    if report["undocumented_endpoints"]:
        for endpoint in report["undocumented_endpoints"]:
            lines.append(f"- {endpoint['service']}: {endpoint['method']} {endpoint['path']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Documented But Missing Endpoints", ""])
    if report["documented_missing_endpoints"]:
        for endpoint in report["documented_missing_endpoints"]:
            sources = ", ".join(endpoint.get("source_files", [])) or "unknown source"
            lines.append(f"- {endpoint['method']} {endpoint['path']} (documented in: {sources})")
    else:
        lines.append("- None")

    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        for error in report["errors"]:
            lines.append(f"- {error}")
    else:
        lines.append("- None")

    lines.append("")
    return "\n".join(lines)
