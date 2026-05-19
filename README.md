# Docs Drift Script

The Docs Drift Script is a lightweight Python CLI that audits API documentation against OpenAPI specs to detect documentation drift.

It compares live OpenAPI endpoints from one or more services with local Markdown or MDX documentation and reports:

- Undocumented endpoints present in the spec but not in docs
- Documented endpoints that no longer exist in the available specs
- Matched endpoints
- Per-service coverage summaries
- Fetch and parsing errors encountered during the audit

## Why It Matters

API documentation loses trust quickly when services evolve faster than the docs that describe them. New endpoints ship, old ones disappear, and teams end up guessing which source is accurate.

This tool gives engineering teams a repeatable way to measure documentation coverage, surface drift early, and keep API docs aligned with reality.

## Features

- Multi-service support
- OpenAPI ingestion over HTTP
- Markdown and MDX parsing
- Undocumented and stale endpoint detection
- Markdown and JSON reports
- Graceful error handling per service
- Configurable CLI overrides

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a YAML config file like this:

```yaml
services:
  service-a:
    base_url: https://api.example.com/service-a
    openapi_path: /openapi.json
  service-b:
    base_url: https://api.example.com/service-b
    openapi_path: /v3/api-docs

docs_path: ./examples/sample_docs
output_path: ./output
request_timeout_seconds: 20
```

Values in the config can also reference environment variables using `${VAR_NAME}` syntax.

## Usage

Run the audit with:

```bash
python -m src.main --config config.yaml --docs ./docs --output ./output --verbose
```

CLI flags:

- `--config`: path to the YAML config file
- `--docs`: override the docs directory from the config file
- `--output`: override the output directory from the config file
- `--verbose`: print progress and service-level errors during execution

## How Matching Works

The tool extracts `(METHOD, PATH)` pairs from:

- OpenAPI `paths` entries for each configured service
- Markdown or MDX files using heuristic text and code block extraction

Comparison is based on normalized endpoint pairs:

- methods are uppercased
- query strings and fragments are ignored
- full URLs found in docs are reduced to their path component
- common parameter styles such as `:id` and `<id>` are normalized to `{id}`

Service matching is explicit for spec-side results:

- each service gets its own matched and undocumented endpoint lists
- documented-but-missing endpoints are computed against the union of successfully fetched service specs

That means stale endpoint detection is most accurate when all configured services are reachable. If one or more services fail, the report still completes, but documented-missing results may be incomplete.

## Example Output

Markdown report excerpt:

```text
Undocumented endpoints:
- service-a: POST /v1/payouts/{payout_id}/cancel
- service-b: GET /v1/payins/{payin_id}

Documented but missing endpoints:
- GET /v1/legacy-payouts
```

The tool also writes a structured JSON report for automation and CI workflows.

## Limitations

- Results depend on the quality and completeness of the OpenAPI specs you provide.
- Documentation extraction is heuristic-based and may miss endpoints expressed only in prose.
- The tool compares endpoint presence and does not validate request bodies, schemas, or business logic correctness.
- It does not attempt to fully understand narrative-only documentation with no recognizable method and path patterns.

## Contributing

Contributions are welcome. If you want to improve parsing, reporting, or OpenAPI support:

1. Open an issue describing the use case or bug.
2. Submit a pull request with tests or reproducible examples where practical.
3. Keep changes focused, documented, and friendly to downstream adopters.

## Repository Layout

```text
api-doc-audit/
├── README.md
├── requirements.txt
├── .gitignore
├── config.example.yaml
├── .env.example
├── src/
│   ├── main.py
│   ├── audit.py
│   ├── services.py
│   ├── docs_parser.py
│   ├── reporting.py
│   └── utils.py
└── examples/
    ├── config.yaml
    ├── sample_docs/
    │   ├── payouts.md
    │   └── payins.md
    └── output/
        ├── drift_report.md
        └── drift_report.json
```
