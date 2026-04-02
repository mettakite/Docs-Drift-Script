"""Service-side helpers for fetching and parsing OpenAPI specs."""

from __future__ import annotations

from typing import Any

import requests

from .utils import EndpointRecord, ServiceConfig, allowed_http_methods, normalize_path


def fetch_service_endpoints(
    service_config: ServiceConfig,
    timeout: int,
    verbose: bool = False,
) -> tuple[list[EndpointRecord], list[str]]:
    """Fetch a service OpenAPI document and extract endpoint records."""
    if verbose:
        print(f"Fetching spec for {service_config.name}: {service_config.spec_url}")

    try:
        response = requests.get(service_config.spec_url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        return [], [f"Failed to fetch OpenAPI spec from {service_config.spec_url}: {exc}"]

    try:
        spec = response.json()
    except ValueError as exc:
        return [], [f"Invalid JSON returned by {service_config.spec_url}: {exc}"]

    try:
        endpoints = extract_openapi_endpoints(spec)
    except ValueError as exc:
        return [], [str(exc)]

    if verbose:
        print(f"Found {len(endpoints)} endpoints in {service_config.name}")

    return endpoints, []


def extract_openapi_endpoints(spec: dict[str, Any]) -> list[EndpointRecord]:
    """Extract normalized endpoint records from an OpenAPI 3.x style document."""
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("OpenAPI document does not contain a valid 'paths' object.")

    endpoints: list[EndpointRecord] = []
    supported_methods = allowed_http_methods()

    for raw_path, operations in paths.items():
        if not isinstance(operations, dict):
            continue
        for method in supported_methods:
            if method.lower() not in operations:
                continue
            endpoints.append(
                EndpointRecord(
                    method=method,
                    path=normalize_path(raw_path),
                    source_file="",
                )
            )

    unique = sorted({(item.method, item.path) for item in endpoints})
    return [
        EndpointRecord(method=method, path=path, source_file="")
        for method, path in unique
    ]
