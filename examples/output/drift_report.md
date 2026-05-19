# API Documentation Drift Report

## Overview

- Generated at: 2026-04-02T00:00:00+00:00
- Services configured: 2
- Services audited: 2
- Spec fetch complete: yes

## Audit Summary

The audit compares endpoint references found in documentation against endpoints defined in the OpenAPI specification(s).

- Number of endpoints cited in documentation: 7
- Number of endpoints defined in OpenAPI specification(s): 8
- Endpoints matched between documentation and specification(s): 6
- Undocumented endpoints: 2
- Documented but missing endpoints: 1
- Documentation parsing errors: 0

## Coverage By Service

| Service | Spec URL | Spec Endpoints | Matched | Undocumented | Coverage |
| --- | --- | ---: | ---: | ---: | ---: |
| service-a | https://api.example.com/service-a/openapi.json | 4 | 3 | 1 | 75.0% |
| service-b | https://api.example.com/service-b/v3/api-docs | 4 | 3 | 1 | 75.0% |

## Undocumented Endpoints

- service-a: POST /v1/payouts/{payout_id}/cancel
- service-b: GET /v1/payins/{payin_id}

## Documented But Missing Endpoints

- GET /v1/legacy-payouts (documented in: payouts.md)

## Errors

- None
