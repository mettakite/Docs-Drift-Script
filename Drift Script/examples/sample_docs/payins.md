# Payins API

The payins API covers inbound payment collection flows.

## Create a payin

Use `POST /v1/payins` to create a payin request.

```bash
curl -X POST https://api.example.com/v1/payins
```

## List payins

The endpoint `GET /v1/payins` returns recent payins.

## Refund a payin

Use `POST /v1/payins/{payin_id}/refund` when a completed payin needs to be reversed.
