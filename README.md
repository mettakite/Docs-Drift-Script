# Detecting Documentation Drift

In most platforms or APIs, documentation is expected to stay accurate as the product evolves. Once an article is published, everyone assumes the right team will update it when the product changes — whether that’s product, engineering, support, or a writing team.

But growing platforms change constantly. A product team updates an endpoint. Engineering adds a new enum. A retry interval changes in configuration. A support team learns about a new edge case. 

Each change may be small, but if it does not make its way back into the docs, the documentation slowly stops matching the product. This gap is referred to as *documentation drift*.

For developers, this is more than an inconvenience. Documentation is often the closest thing they have to a source of truth. When it falls out of sync with how the platform behaves, integrations become harder to build, support teams spend more time answering avoidable questions, and trust in the platform starts to erode.

This project started with a simple question: Can documentation drift be detected before users find it?

## What this project shows

This project demonstrates my ability to:

- Identify documentation quality problems across large platforms.
- Work with OpenAPI specifications, Markdown, MDX, and docs-as-code workflows.
- Build repeatable QA processes for documentation accuracy.
- Translate technical drift into reviewable reports for writers, engineers, product teams, and SMEs.
- Think about documentation as content that supports both developers and AI-assisted retrieval.

I also used ChatGPT, Claude Code, and GitHub Copilot as development and review aids while building this script. I used them to reason through parsing approaches, test edge cases, improve report wording, and review sample output for clarity.

AI helped speed up iteration, but the core decisions were still human-led: defining the problem, deciding what the audit should flag, reviewing false positives, validating audit results, shaping the report output, and determining how writers, engineers, product teams, and SMEs could use the results.

## Problem

As a technical writer working on large, fast-moving platforms, I kept running into the same problem — existing documentation did not always match how the platform actually behaved.

One example was webhook retry behavior.

Documentation said failed webhook events were retried over a one-hour period. In practice, the platform retried them every five minutes based on how the service was configured.

That kind of mismatch may seem small, but it can create real problems for developers. If a team builds their integration around the documented retry behavior, they may design the wrong monitoring, alerting, or fallback logic.

This was not just a one-off documentation bug. It pointed to a larger problem:

- Documentation and platform behavior were not tightly connected.
- Backend changes did not always make their way into documentation.
- Writers, engineers, product managers, and support teams did not have a shared way to detect drift.
- There was no repeatable process for finding these mismatches before users ran into them.

## Impact

For developers, documentation is often the source of truth. They use it to decide how to build an integration, what values to send, what errors to handle, and what behavior to expect from the platform.

When the docs are wrong, the impact spreads quickly:

- Developers build against outdated or incorrect information.
- Integrations take longer to debug.
- Support teams spend more time answering avoidable questions.
- Product and engineering teams lose visibility into where documentation no longer matches the platform.
- Customers lose confidence in the platform when it does not behave the way it is described.

The issue is not just that a page is out of date. The larger problem is that no one can easily tell where the documentation has drifted until a user runs into it.

## Approach

Manual review was not enough. A writer or subject matter expert (SME) could review one page, or even a small group of pages, but that did not solve the larger problem. Documentation covered too many endpoints, enums, workflows, and edge cases to reliably check by hand every time the platform changed.

I wanted a repeatable way to compare what the docs said against what the OpenAPI specification defined, and what the OpenAPI specification included that the docs did not yet cover.

I built a script that compares two sources:

- **OpenAPI specification**: The structured source for endpoints, request fields, response fields, enums, and other details about the platform’s API.
- **Documentation content**: The articles, diagrams, quickstarts, and support content developers use to understand the platform.

The goal was simple — identify mismatches at scale so writers, engineers, and product teams could review and fix them before users ran into them.

## Docs Audit script

To address this gap, I built a *Docs Audit script*.

The script compares the local OpenAPI specification with the Markdown articles in the documentation repository and looks for places where the two no longer match.

At a high level, the script does four things:

1. **Reads the OpenAPI specification**: The script parses the API specification to collect the endpoints, request fields, response fields, enums, and other values that define the current version of the API.

2. **Scans the documentation content**: The script scans the Markdown files in the documentation repository for references to endpoints, fields, enums, and other API details that appear in guides, quickstarts, reference pages, and other support content.

3. **Compares the two sources**: The script checks whether the documentation references values that are missing from the OpenAPI specification, and whether the OpenAPI specification includes values that are missing from the docs.

4. **Generates reviewable reports**: The script outputs CSV and Markdown reports so writers, engineers, and product teams can review the results and decide what needs to be fixed and where.

The audit flags issues such as:

- Endpoints referenced in the docs but missing from the OpenAPI specification.
- Endpoints defined in the OpenAPI specification but not documented.
- Enum values in the docs that no longer exist in the OpenAPI specification.
- Enum values in the OpenAPI specification that are missing from the docs.
- Fields or values that may need review because the docs and specification do not agree.

This audit is best understood as a cross-reference audit. It does not assume every OpenAPI endpoint must appear in a guide. Instead, it shows which API operations are explicitly referenced in documentation and which references may need review.

The goal was not to automatically rewrite documentation. The goal was to make drift visible, reviewable, and easier to scope and prioritize.

### Using the script

To use the script:
1. Clone or download the repo: https://github.com/mettakite/Docs-Drift-Script
2. Copy the *Docs-Drift-Script* folder into your Docusaurus project (further platform compatibility planned: e.g. Redocly, ReadMe, etc.)
3. Open **Terminal** and navigate to your Docusaurus project 
    - e.g. `cd "/path/to/your/Docusaurus/project/"`
4. Run the following commands:
    1. `python3 -m venv .venv`
    2. `source .venv/bin/activate`
    3. `pip install -r requirements.txt`
    4. `python3 -m src.main --config config.yaml --docs ../../docs --output ./output --verbose`
5. The script compares the local OpenAPI specification with the Markdown articles and returns a summary of the results in the terminal window:

> Terminal summary

```shell
Scanning docs in ../../docs
Reading local spec for acme-api: /docs/static/openapi/acme.yaml
Found 48 endpoints in acme-api
Audit complete: 1 service audited, 9 matched, 39 not cited in narrative docs, 3 narrative references missing from OpenAPI.
Markdown report: output/drift_report.md
CSV report: output/drift_report.csv
JSON report: output/drift_report.json
```

The [Reports](#reports) breaking down the results can be found in the **tools** > **api-doc-audit** > **output** folder. 

## Features

- Multi-service support
- OpenAPI ingestion over HTTP
- Markdown and MDX parsing
- Undocumented and stale endpoint detection
- Markdown, JSON, and CSV reports
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

## Audit results

The first audit flagged more than 500 potential inconsistencies across roughly 300 articles.

Not every flagged item represented a confirmed issue with documentation. Some results required review because API terms can appear in examples, changelogs, migration notes, or legacy references. But the audit made those possible mismatches visible in one place instead of leaving teams to find them manually.

The most common issues included:

- **Enums in the docs that were missing from the OpenAPI specification**: These needed review to confirm whether the docs were outdated, the OpenAPI specification was incomplete, or the value was only valid in a legacy workflow.

- **OpenAPI enum values that were missing from the docs**: These pointed to places where the platform supported values that were not clearly documented for developers.

- **Endpoints referenced in the docs but missing from the OpenAPI specification**: These helped identify outdated links, legacy workflows, or content that no longer matched the platform’s API.

- **Endpoints defined in the OpenAPI specification but not covered in the docs**: These helped identify possible gaps or endpoints that had not yet been documented.

The value of the report was not just the number of issues it found. It gave writers, engineers, product teams, and SMEs a shared review list to scope and prioritize cleanup.

### Reports

The script generates three reports. The sample reports below use sanitized data; the structure mirrors the real audit output, but endpoint names, service names, file paths, and counts have been changed for confidentiality.

Available reports include:
- **drift_report.md**: A human-readable Markdown report that summarizes the inconsistencies the script found.
- **drift_report.json**: A machine-readable report that can be used in CI/CD pipelines or other automated workflows.
- **drift_report.csv**: A CSV report that can be opened in Excel for filtering, triage, planning, and scoping.

#### Report examples

<details>
<summary><h3>Markdown report</h3></summary>

<h1>API Documentation Drift Report</h1>

<h2>Overview</h2>

- Generated at: 2026-05-19T07:32:56+00:00
- Services configured: 1
- Services audited: 1
- Spec read complete: yes

<h2>Executive Summary</h2>

This audit compares endpoint references in narrative documentation with endpoints defined in the OpenAPI specification. In this documentation site, the API reference is generated from the OpenAPI file, so this report is best read as a cross-reference audit: it shows which API operations are explicitly cited in guides and which guide references may need review.

- OpenAPI operations reviewed: 48
- Endpoint references detected in narrative docs: 12
- Narrative references matched to OpenAPI operations: 9
- OpenAPI operations not cited in narrative docs: 39
- Narrative references missing from OpenAPI: 3
- Narrative cross-reference rate: 18.8%
- Detected doc-reference accuracy: 75.0%

<h2>Audit Summary</h2>

The counts below distinguish between generated API reference coverage and explicit mentions in Markdown or MDX guide content.

- Endpoint references detected in narrative documentation: 12
- Endpoints defined in OpenAPI specification: 48
- Endpoint references matched between narrative docs and specification: 9
- OpenAPI endpoints not cited in narrative docs: 39
- Narrative doc references missing from OpenAPI specification: 3
- Documentation parsing errors: 0

<h2>Report Files</h2>

- `drift_report.md`: human-readable summary and representative findings
- `drift_report.csv`: complete endpoint-level export for sorting, filtering, and review
- `drift_report.json`: structured report for automation

<h2>Coverage By Service</h2>

| Service | Spec Source | OpenAPI Operations | Matched Narrative References | Not Cited In Narrative Docs | Cross-Reference Rate |
| --- | --- | ---: | ---: | ---: | ---: |
| acme-api | docs/static/openapi/acme.yaml | 48 | 9 | 39 | 18.8% |

<h2>Matched Endpoint References</h2>

- GET /api/v1/customers/{customerId} (source: docs/customers/get-customer.md)
- POST /api/v1/customers (source: docs/customers/create-customer.md)
- POST /api/v1/payments (source: docs/payments/create-payment.md)
- GET /api/v1/payments/{paymentId} (source: docs/payments/get-payment.md)
- POST /api/v1/refunds (source: docs/refunds/create-refund.md)
- GET /api/v1/refunds/{refundId} (source: docs/refunds/get-refund.md)
- POST /api/v1/webhooks/subscriptions (source: docs/webhooks/subscribe-to-events.md)
- DELETE /api/v1/webhooks/subscriptions/{subscriptionId} (source: docs/webhooks/manage-subscriptions.md)
- GET /api/v1/reports/{reportId} (source: docs/reports/get-report.md)

<h2>OpenAPI Endpoints Not Cited In Narrative Docs</h2>

These endpoints are defined in the OpenAPI specification. They may still appear in the generated API reference, but the parser did not find explicit Markdown/MDX guide references for them.

- acme-api: GET /api/v1/accounts
- acme-api: GET /api/v1/accounts/{accountId}
- acme-api: POST /api/v1/accounts
- acme-api: PATCH /api/v1/accounts/{accountId}
- acme-api: GET /api/v1/customers
- acme-api: PATCH /api/v1/customers/{customerId}
- acme-api: DELETE /api/v1/customers/{customerId}
- acme-api: GET /api/v1/payment-methods
- acme-api: POST /api/v1/payment-methods
- acme-api: DELETE /api/v1/payment-methods/{paymentMethodId}
- 29 additional endpoints omitted from Markdown; see `drift_report.csv` for the complete list.

<h2>Narrative Doc References Missing From OpenAPI</h2>

These endpoint references appear in Markdown/MDX guide content but were not found in the OpenAPI specification. They are good candidates for cleanup, redirect checks, or spec validation.

- GET /api/v1/legacy-payments/{paymentId} (source: docs/payments/legacy-payments.md)
- POST /api/v1/customers/{customerId}/verify (source: docs/customers/verify-customer.md)
- GET /api/v1/reports/export (source: docs/reports/export-reports.md)

<h2>Recommended Next Steps</h2>

- Review the 3 narrative doc references missing from OpenAPI first; these are the highest-signal candidates for stale paths, redirects, or spec gaps.
- Use `drift_report.csv` to triage the 39 OpenAPI operations not cited in narrative docs by issue type, coverage status, method, and path.
- Treat generated API reference coverage separately from narrative guide coverage; this report focuses on explicit guide references.

<h2>Errors</h2>

- None

</details>

<details>

<summary><h3>JSON report</h3></summary>

```json
{
  "generated_at": "2026-05-19T07:32:56+00:00",
  "summary": {
    "services_configured": 1,
    "services_audited": 1,
    "spec_fetch_complete": true,
    "documented_endpoint_count": 12,
    "spec_endpoint_count": 48,
    "matched_endpoint_count": 9,
    "undocumented_endpoint_count": 39,
    "documented_missing_endpoint_count": 3,
    "docs_errors_count": 0
  },
  "services": [
    {
      "service": "acme-api",
      "spec_url": "docs/static/openapi/acme.yaml",
      "spec_endpoint_count": 48,
      "matched_count": 9,
      "undocumented_count": 39,
      "coverage_percentage": 18.8,
      "matched_endpoints": [
        {
          "method": "POST",
          "path": "/api/v1/customers",
          "service": "acme-api",
          "source_files": [
            "docs/customers/create-customer.md"
          ]
        },
        {
          "method": "POST",
          "path": "/api/v1/payments",
          "service": "acme-api",
          "source_files": [
            "docs/payments/create-payment.md"
          ]
        }
      ],
      "documented_missing_endpoints": [
        {
          "method": "GET",
          "path": "/api/v1/legacy-payments/{paymentId}",
          "source_files": [
            "docs/payments/legacy-payments.md"
          ]
        }
      ],
      "errors": []
    }
  ]
}
```

</details>

<details>

<summary><h3>CSV report</h3></summary>

```csv
service,issue_type,method,path,source_file,notes
acme-api,matched_reference,POST,/api/v1/customers,docs/customers/create-customer.md,Reference matched OpenAPI specification
acme-api,missing_from_openapi,GET,/api/v1/legacy-payments/{paymentId},docs/payments/legacy-payments.md,Reference appears in docs but not OpenAPI
acme-api,not_cited_in_docs,POST,/api/v1/webhooks/subscriptions,,Endpoint exists in OpenAPI but was not cited in narrative docs
```

</details> 

## Resulting changes

The audit script report gave the team a more repeatable way to manage documentation quality.

Before the script, drift was corrected when an inconsistency was found, an engineer flagged a page, or a customer ran into a problem. With the audit report, teams had a shared report they could use to review mismatches, assign follow-up work, and prioritize cleanup.

The biggest changes were:

- **Better visibility**: Writers, engineers, product managers, and SMEs could see where docs and the OpenAPI specification did not agree.
- **Clearer prioritization**: Teams could scope appropriately and focus first on issues that affected active endpoints, supported enum values, or high-traffic documentation.
- **More productive reviews**: Instead of asking teams to manually review large sections of documentation, the audit gave them a focused list of items to verify.
- **A foundation for ongoing validation**: The same approach could be run again as the platform changed, making drift easier to catch over time.

The main change was not just cleaner documentation. It was a better workflow for keeping documentation aligned with the platform as it grew and evolved.

## Planned improvements

The first version of the audit focused on comparing documentation against the OpenAPI specification. That was enough to make drift visible, but there are several ways to extend this tool:

- **Run the audit in a CI/CD pipeline**: Add the audit to the documentation publishing pipeline so teams can catch endpoint, field, and enum mismatches before changes are merged and pushed live.

- **Compare against live or pre-production behavior**: OpenAPI specifications are useful, but they do not always capture every behavior developers care about. Future versions can validate selected workflows against live or pre-production services.

- **Add severity levels**: Not every mismatch has the same impact. The audit could rank issues based on whether they affect active endpoints, required fields, supported enum values, high-traffic pages, or developer-facing workflows.

- **Improve reporting for cross-functional review**: The reports could group issues by product area, endpoint, documentation page, owner, or priority so writers, engineers, product managers, and SMEs can review them faster.

- **Extend the audit to AI-assisted support and search**: As teams use LLM-based tools to answer questions from documentation, source content needs to be structured, accurate, and easy to retrieve. The same approach could help identify documentation gaps that lead to incorrect AI-generated answers.

## Limitations

- Results depend on the quality and completeness of the OpenAPI specifications you provide.
- Documentation extraction is heuristic-based and may miss endpoints expressed only in prose.
- The tool compares endpoint presence and does not validate request bodies, schemas, or business logic correctness.
- It does not attempt to fully understand narrative-only documentation with no recognizable method and path patterns.

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

## Closing

Documentation quality is not only a writing problem. It is also a maintenance problem.

As platforms grow, the number of endpoints, fields, enum values, workflows, and edge cases grows with them. Without a repeatable way to check whether the docs still match the platform, drift becomes almost inevitable.

This project started as my attempt to make that problem visible.

The script does not replace writers, engineers, product managers, or SMEs. It gives them a better starting point: a shared report that shows where the docs may need review, what changed, and where to focus first.

Good documentation still depends on good judgment. But that judgment is stronger when teams can measure, validate, scope, and prioritize the work in front of them.
