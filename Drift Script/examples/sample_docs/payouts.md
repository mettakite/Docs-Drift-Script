# Payouts API

The payouts API lets clients create, inspect, and manage payout requests.

## Create a payout

Use `POST /v1/payouts` to create a new payout.

```http
POST /v1/payouts
Content-Type: application/json
```

## List payouts

Use `GET /v1/payouts` to retrieve a paginated list of payouts.

## Retrieve a payout

Call `GET /v1/payouts/{payout_id}` to fetch a single payout record.

## Legacy reference

Older guides may still mention `GET /v1/legacy-payouts`, but new integrations should avoid it.
