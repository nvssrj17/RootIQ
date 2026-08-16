# Incident 001 — Order Retrieval Failure

## Symptom

The `/health` endpoint returns successfully, but retrieving an order through
`GET /orders/1` returns an Internal Server Error.

## Observed Behavior

- `GET /health` → 200 OK
- `GET /orders/1` → 500 Internal Server Error

## Relevant Log Evidence

The application log reports:

`sqlite3.OperationalError: no such column: orders.customer_email`

## Investigation Goal

Determine why the order retrieval endpoint is failing and identify the
underlying root cause.

## Status

Intentionally reproduced for RootIQ evaluation.