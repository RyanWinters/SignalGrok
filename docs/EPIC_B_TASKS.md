# Epic B — Webhook Intake Task Plan

This checklist breaks Epic B from `ARCHITECTURE.md` into implementation-sized tasks with clear completion criteria.

## Goal
Deliver a production-ready, authenticated webhook intake flow that validates and normalizes inbound alerts, enforces idempotency, persists raw payloads, and is covered by automated tests.

## Task Checklist

### B1 — Implement authenticated webhook endpoint
- [ ] Keep `POST /webhooks/trading-alert` as the intake endpoint.
- [ ] Enforce `X-SignalGrok-Key` header auth against configured secret.
- [ ] Return `401` for invalid/missing key and avoid leaking secret details.
- [ ] Emit structured logs with request metadata and outcome.

**Done when**
- Endpoint requires valid auth key in all environments.
- Happy-path response shape is stable and documented.

### B2 — Add payload schema + normalization pipeline
- [ ] Expand Pydantic schema for expected upstream payload fields (required + optional).
- [ ] Define normalized alert contract (ticker casing, signal type normalization, direction mapping, timestamp parsing).
- [ ] Add a pure normalization function/service returning a DB-ready object.
- [ ] Reject invalid payloads with `422` and actionable validation errors.

**Done when**
- Normalization is deterministic and unit-tested.
- API response uses normalized ticker/signal values.

### B3 — Add idempotency handling
- [ ] Use `(webhook_endpoint_id, external_alert_id)` as idempotency key.
- [ ] Add DB constraint/index to enforce uniqueness when `external_alert_id` is present.
- [ ] Handle duplicate alerts safely (no duplicate processing side effects).
- [ ] Return deterministic API behavior for duplicates (ack with duplicate marker or no-op accepted response).

**Done when**
- Replayed webhook requests do not create duplicate alert records.
- Duplicate handling behavior is explicitly tested and documented.

### B4 — Persist raw alerts to `incoming_alerts`
- [ ] Add/adjust migration(s) for `incoming_alerts` fields used by intake.
- [ ] Insert alert rows immediately after auth + schema validation.
- [ ] Store full raw payload JSON and normalized fields (`ticker`, `signal_type`, `direction`, etc.).
- [ ] Set initial status to `RECEIVED` and track `received_at` timestamp.

**Done when**
- Every accepted request is auditable from DB row to raw payload.
- Persistence failures surface as `5xx` and are logged with context.

### B5 — Add test coverage (unit + integration)
- [ ] Unit tests for schema validation and normalization helpers.
- [ ] Integration test for successful authenticated intake and DB persistence.
- [ ] Integration test for invalid key (`401`).
- [ ] Integration test for idempotency duplicate path.
- [ ] Integration test for malformed payload (`422`).

**Done when**
- Test suite covers success and major failure paths for Epic B.
- CI runs these tests on each PR.

## Suggested Implementation Order
1. B2 (schema + normalization)
2. B4 (persistence)
3. B3 (idempotency)
4. B1 final polish (auth/logging behavior)
5. B5 tests and regression hardening

## Deliverables
- Updated webhook route and service layer for intake.
- Migration(s) for idempotency + incoming alert persistence.
- Automated tests for success/auth failure/validation/idempotency.
- Updated docs describing request contract and duplicate handling.
