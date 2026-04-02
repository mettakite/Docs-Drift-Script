# API Documentation Drift Report

## Overview

- Generated at: 2026-04-02T00:00:00+00:00
- Services configured: 2
- Services audited: 2
- Spec fetch complete: yes

## Summary

- Documented endpoints found in docs: 7
- Endpoints found in available specs: 8
- Matched endpoints: 6
- Undocumented endpoints: 2
- Documented but missing endpoints: 1
- Docs parsing errors: 0

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
