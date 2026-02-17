# SignalGrok — Initial Architecture Blueprint

## 1) End-to-End Data Flow

1. **Inbound alert enters FastAPI webhook endpoint**
   - A provider (TradingView, custom bot, broker alert engine) sends JSON to `POST /webhooks/trading-alert`.
   - Request includes HMAC/API key header (`X-SignalGrok-Key`) for authentication.
2. **FastAPI validates payload + auth key**
   - Pydantic schema validates required fields (`ticker`, `signal`, etc.).
   - Invalid requests are rejected with `401` or `422`.
3. **Alert is persisted as `RECEIVED`**
   - API writes an `incoming_alerts` row immediately for auditing/replay.
4. **News context lookup (Finnhub)**
   - Worker/service calls Finnhub company-news endpoint for recent ticker news.
   - Response is normalized into concise summaries and sentiment cues.
5. **LLM decision step (OpenAI)**
   - Alert + normalized news are sent to the LLM with a deterministic prompt.
   - Model returns: alignment verdict (`ALLOW`/`BLOCK`), confidence, rationale, extracted sentiment.
6. **Decision is persisted in SQL**
   - Save model metadata, prompt hash/version, confidence, and final decision.
7. **Conditional forward to Discord**
   - If decision is `ALLOW` and confidence is above threshold, send a formatted Discord webhook message.
   - Save dispatch status (`SENT`, `FAILED`) and Discord response metadata.
8. **Observability and retries**
   - Failed Finnhub/OpenAI/Discord calls are retried with exponential backoff and dead-letter handling.

## 2) Database Schema (PostgreSQL)

### `users`
- `id` (uuid, pk)
- `email` (text, unique, not null)
- `password_hash` (text, not null)
- `plan_tier` (text, not null, default `free`)
- `is_active` (bool, not null, default true)
- `created_at` (timestamptz, not null)
- `updated_at` (timestamptz, not null)

### `webhook_endpoints`
- `id` (uuid, pk)
- `user_id` (uuid, fk -> users.id, indexed)
- `name` (text, not null)
- `source_type` (text, not null) — e.g., `tradingview`, `custom`
- `secret_key_hash` (text, not null)
- `is_active` (bool, not null, default true)
- `created_at` (timestamptz, not null)
- `updated_at` (timestamptz, not null)

### `incoming_alerts`
- `id` (uuid, pk)
- `webhook_endpoint_id` (uuid, fk -> webhook_endpoints.id, indexed)
- `external_alert_id` (text, nullable)
- `raw_payload` (jsonb, not null)
- `ticker` (text, not null, indexed)
- `signal_type` (text, not null) — e.g., `MACD_CROSSOVER`
- `direction` (text, nullable) — `bullish`/`bearish`
- `status` (text, not null) — `RECEIVED`, `PROCESSED`, `ERROR`
- `received_at` (timestamptz, not null)

### `llm_decisions`
- `id` (uuid, pk)
- `incoming_alert_id` (uuid, fk -> incoming_alerts.id, unique)
- `model_name` (text, not null)
- `prompt_version` (text, not null)
- `news_context` (jsonb, not null)
- `decision` (text, not null) — `ALLOW`/`BLOCK`
- `confidence` (numeric(5,4), not null)
- `reasoning_summary` (text, not null)
- `latency_ms` (int, nullable)
- `created_at` (timestamptz, not null)

### `discord_dispatches`
- `id` (uuid, pk)
- `incoming_alert_id` (uuid, fk -> incoming_alerts.id, indexed)
- `llm_decision_id` (uuid, fk -> llm_decisions.id, indexed)
- `webhook_url_ref` (text, not null) — encrypted/tokenized reference, never raw URL in plaintext logs
- `delivery_status` (text, not null) — `SENT`, `FAILED`, `SKIPPED`
- `http_status_code` (int, nullable)
- `response_body` (text, nullable)
- `sent_at` (timestamptz, nullable)
- `created_at` (timestamptz, not null)

## 3) Epics & Sequential Tasks

### Epic A — Platform Foundations
1. Initialize repository structure (`app/`, `tests/`, `migrations/`).
2. Add config module (`pydantic-settings`) with env var validation.
3. Set up logging, request IDs, and structured JSON logs.
4. Add Docker + docker-compose for FastAPI + PostgreSQL.

### Epic B — Webhook Intake
1. Implement authenticated webhook endpoint.
2. Add Pydantic schemas and payload normalization.
3. Add idempotency handling using `external_alert_id` + endpoint.
4. Persist raw alerts to `incoming_alerts`.
5. Write unit and integration tests for success + auth failures.

Detailed Epic B execution checklist: `docs/EPIC_B_TASKS.md`.

### Epic C — Market News Integration (Finnhub)
1. Build Finnhub client with retries/timeouts.
2. Create news normalization and deduplication logic.
3. Add circuit breaker/fallback when Finnhub is down.
4. Persist fetched news context in `llm_decisions` input snapshot.

### Epic D — LLM Sentiment Decision Engine
1. Create prompt templates with explicit JSON schema outputs.
2. Implement OpenAI client wrapper with timeout/retry controls.
3. Parse and validate LLM output into strong typed model.
4. Persist decision, confidence, and rationale.
5. Add threshold gating config (global + per-user override).

### Epic E — Discord Dispatch
1. Build Discord webhook dispatcher client.
2. Format outbound message with alert + decision context.
3. Dispatch only when `ALLOW` and confidence ≥ threshold.
4. Persist dispatch result + HTTP status.
5. Add retry + dead-letter for transient failures.

### Epic F — Billing, Multi-Tenancy, and Operations
1. Introduce users, API keys, and tenant scoping.
2. Add usage metering (alerts processed, LLM calls, dispatches).
3. Integrate Stripe for subscription tiers and quota enforcement.
4. Add admin dashboard + audit trail exports.
5. Production hardening: rate limits, WAF, Sentry, dashboards, alerts.

## 4) FastAPI Boilerplate Contract

- Endpoint: `POST /webhooks/trading-alert`
- Header auth: `X-SignalGrok-Key`
- Validates payload with Pydantic
- Prints normalized ticker to console
- Returns ack JSON (`status`, `ticker`)

> Implemented in `main.py` as the initial bootstrap.
