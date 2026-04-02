"""Shared models and utility helpers."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import yaml


@dataclass(frozen=True)
class EndpointRecord:
    """A normalized endpoint record extracted from docs or specs."""

    method: str
    path: str
    source_file: str


@dataclass(frozen=True)
class ServiceConfig:
    """Service configuration loaded from YAML."""

    name: str
    base_url: str
    openapi_path: str

    @property
    def spec_url(self) -> str:
        """Return the full OpenAPI URL for the service."""
        if self.openapi_path.startswith(("http://", "https://")):
            return self.openapi_path
        return urljoin(self.base_url.rstrip("/") + "/", self.openapi_path.lstrip("/"))


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and validate a YAML config file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw_text = config_path.read_text(encoding="utf-8")
    expanded_text = os.path.expandvars(raw_text)
    data = yaml.safe_load(expanded_text) or {}

    if not isinstance(data, dict):
        raise ValueError("Config file must contain a top-level mapping.")
    if "services" not in data or not isinstance(data["services"], dict) or not data["services"]:
        raise ValueError("Config must define at least one service under 'services'.")
    if "docs_path" not in data:
        raise ValueError("Config must define 'docs_path'.")
    if "output_path" not in data:
        raise ValueError("Config must define 'output_path'.")

    if "request_timeout_seconds" not in data:
        data["request_timeout_seconds"] = 20

    return data


def load_service_configs(config: dict[str, Any]) -> list[ServiceConfig]:
    """Convert raw config data into service config objects."""
    services: list[ServiceConfig] = []
    for name, values in config["services"].items():
        if not isinstance(values, dict):
            raise ValueError(f"Service '{name}' must be a mapping.")
        base_url = values.get("base_url")
        openapi_path = values.get("openapi_path")
        if not base_url or not openapi_path:
            raise ValueError(
                f"Service '{name}' must define both 'base_url' and 'openapi_path'."
            )
        services.append(
            ServiceConfig(
                name=str(name),
                base_url=str(base_url),
                openapi_path=str(openapi_path),
            )
        )
    return services


def normalize_method(method: str) -> str:
    """Normalize an HTTP method for comparison."""
    return method.strip().upper()


def normalize_path(path: str) -> str:
    """Normalize a path or URL for endpoint comparison."""
    value = path.strip().strip("`'\"").rstrip(".,;:")

    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        value = parsed.path or "/"
    else:
        value = value.split("?", 1)[0].split("#", 1)[0]

    value = re.sub(r"\{+\s*([^}/\s]+)\s*\}+", r"{\1}", value)
    value = re.sub(r"<\s*([^>/\s]+)\s*>", r"{\1}", value)
    value = re.sub(r":([A-Za-z_][A-Za-z0-9_-]*)", r"{\1}", value)
    value = re.sub(r"/{2,}", "/", value)

    if not value.startswith("/"):
        value = "/" + value.lstrip("/")
    if len(value) > 1:
        value = value.rstrip("/")

    return value


def allowed_http_methods() -> tuple[str, ...]:
    """Return supported HTTP methods in uppercase form."""
    return ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD")


def current_timestamp() -> str:
    """Return a UTC ISO-8601 timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_directory(path: Path) -> None:
    """Create a directory if it does not already exist."""
    path.mkdir(parents=True, exist_ok=True)


def build_endpoint_entry(
    method: str,
    path: str,
    service: str | None = None,
    source_files: list[str] | None = None,
) -> dict[str, Any]:
    """Build a report-friendly endpoint payload."""
    entry: dict[str, Any] = {"method": method, "path": path}
    if service is not None:
        entry["service"] = service
    if source_files is not None:
        entry["source_files"] = source_files
    return entry


def endpoint_sort_key(item: tuple[str, str]) -> tuple[str, str]:
    """Sort endpoints by method then path."""
    return item[0], item[1]
