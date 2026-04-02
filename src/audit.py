"""Audit workflow for comparing docs with OpenAPI specs."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .docs_parser import parse_docs_directory
from .services import fetch_service_endpoints
from .utils import (
    ServiceConfig,
    build_endpoint_entry,
    current_timestamp,
    endpoint_sort_key,
    load_service_configs,
)


def run_audit(config: dict[str, Any], verbose: bool = False) -> dict[str, Any]:
    """Run the full audit and return a structured report payload."""
    service_configs = load_service_configs(config)
    docs_path = config["docs_path"]
    timeout = int(config.get("request_timeout_seconds", 20))

    if verbose:
        print(f"Scanning docs in {docs_path}")
    documented_records, docs_errors = parse_docs_directory(docs_path)

    docs_sources: dict[tuple[str, str], set[str]] = defaultdict(set)
    for record in documented_records:
        docs_sources[(record.method, record.path)].add(record.source_file)

    docs_endpoint_keys = set(docs_sources)

    service_results: list[dict[str, Any]] = []
    all_spec_keys: set[tuple[str, str]] = set()
    matched_entries: list[dict[str, Any]] = []
    undocumented_entries: list[dict[str, Any]] = []
    service_errors_present = False

    for service_config in service_configs:
        result = _audit_service(
            service_config=service_config,
            docs_endpoint_keys=docs_endpoint_keys,
            docs_sources=docs_sources,
            timeout=timeout,
            verbose=verbose,
        )
        service_results.append(result)

        if result["errors"]:
            service_errors_present = True
        else:
            for endpoint in result["all_spec_endpoints"]:
                all_spec_keys.add((endpoint["method"], endpoint["path"]))

        matched_entries.extend(result["matched_endpoints"])
        undocumented_entries.extend(result["undocumented_endpoints"])

    documented_missing_entries = [
        build_endpoint_entry(
            method=method,
            path=path,
            source_files=sorted(docs_sources[(method, path)]),
        )
        for method, path in sorted(docs_endpoint_keys - all_spec_keys, key=endpoint_sort_key)
    ]

    summary = {
        "services_configured": len(service_configs),
        "services_audited": len(service_results),
        "services_with_errors": sum(1 for result in service_results if result["errors"]),
        "spec_fetch_complete": not service_errors_present,
        "documented_endpoint_count": len(docs_endpoint_keys),
        "spec_endpoint_count": len(all_spec_keys),
        "matched_endpoint_count": len(matched_entries),
        "undocumented_endpoint_count": len(undocumented_entries),
        "documented_missing_endpoint_count": len(documented_missing_entries),
        "docs_errors_count": len(docs_errors),
    }

    top_level_errors = list(docs_errors)
    for result in service_results:
        for message in result["errors"]:
            top_level_errors.append(f"{result['service']}: {message}")

    report = {
        "generated_at": current_timestamp(),
        "summary": summary,
        "services": [
            {
                key: value
                for key, value in result.items()
                if key != "all_spec_endpoints"
            }
            for result in service_results
        ],
        "undocumented_endpoints": undocumented_entries,
        "documented_missing_endpoints": documented_missing_entries,
        "matched_endpoints": matched_entries,
        "errors": top_level_errors,
    }
    return report


def _audit_service(
    service_config: ServiceConfig,
    docs_endpoint_keys: set[tuple[str, str]],
    docs_sources: dict[tuple[str, str], set[str]],
    timeout: int,
    verbose: bool,
) -> dict[str, Any]:
    """Fetch one service spec, compare it to docs, and return service results."""
    spec_endpoints, errors = fetch_service_endpoints(
        service_config=service_config,
        timeout=timeout,
        verbose=verbose,
    )

    spec_endpoint_keys = {(endpoint.method, endpoint.path) for endpoint in spec_endpoints}
    matched_keys = spec_endpoint_keys & docs_endpoint_keys
    undocumented_keys = spec_endpoint_keys - docs_endpoint_keys

    matched_endpoints = [
        build_endpoint_entry(
            method=method,
            path=path,
            service=service_config.name,
            source_files=sorted(docs_sources[(method, path)]),
        )
        for method, path in sorted(matched_keys, key=endpoint_sort_key)
    ]
    undocumented_endpoints = [
        build_endpoint_entry(
            method=method,
            path=path,
            service=service_config.name,
        )
        for method, path in sorted(undocumented_keys, key=endpoint_sort_key)
    ]

    coverage_percentage = round(
        (len(matched_keys) / len(spec_endpoint_keys) * 100) if spec_endpoint_keys else 0.0,
        2,
    )

    return {
        "service": service_config.name,
        "spec_url": service_config.spec_url,
        "spec_endpoint_count": len(spec_endpoint_keys),
        "matched_count": len(matched_keys),
        "undocumented_count": len(undocumented_keys),
        "coverage_percentage": coverage_percentage,
        "matched_endpoints": matched_endpoints,
        "undocumented_endpoints": undocumented_endpoints,
        "errors": errors,
        "all_spec_endpoints": [
            {"method": endpoint.method, "path": endpoint.path}
            for endpoint in sorted(spec_endpoints, key=lambda item: (item.method, item.path))
        ],
    }
