"""CLI entry point for API Doc Audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import run_audit
from .reporting import write_json_report, write_markdown_report
from .utils import load_config


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Audit API documentation against OpenAPI specs.",
    )
    parser.add_argument(
        "--config",
        default="config.example.yaml",
        help="Path to the YAML configuration file.",
    )
    parser.add_argument(
        "--docs",
        help="Override the docs path from the configuration file.",
    )
    parser.add_argument(
        "--output",
        help="Override the output path from the configuration file.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress and service-level errors.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the CLI program."""
    args = parse_args()
    config_path = Path(args.config)

    try:
        config = load_config(config_path)
    except Exception as exc:  # pragma: no cover - CLI error handling
        print(f"Failed to load config: {exc}", file=sys.stderr)
        return 1

    if args.docs:
        config["docs_path"] = args.docs
    if args.output:
        config["output_path"] = args.output

    report = run_audit(config=config, verbose=args.verbose)

    output_dir = Path(config["output_path"])
    markdown_path = write_markdown_report(report, output_dir)
    json_path = write_json_report(report, output_dir)

    summary = report["summary"]
    print(
        "Audit complete: "
        f"{summary['services_audited']} services audited, "
        f"{summary['matched_endpoint_count']} matched, "
        f"{summary['undocumented_endpoint_count']} undocumented, "
        f"{summary['documented_missing_endpoint_count']} documented-but-missing.",
    )
    print(f"Markdown report: {markdown_path}")
    print(f"JSON report: {json_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
