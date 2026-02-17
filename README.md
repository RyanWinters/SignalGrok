# SignalGrok

SignalGrok ingests trading alerts via webhook and normalizes them for downstream processing.

## Local development

```bash
uvicorn app.main:app --reload
```

## Docker development

Start API + Postgres with Docker Compose:

```bash
docker compose up --build
```

The API runs at `http://localhost:8000` and receives `DATABASE_URL` from the compose network:

`postgresql+psycopg://signalgrok:signalgrok@postgres:5432/signalgrok`

### Health and database connection checks

Check API health:

```bash
curl -f http://localhost:8000/health
```

Check API database connectivity:

```bash
curl -f http://localhost:8000/health/database
```

Check Postgres health from compose:

```bash
docker compose exec postgres pg_isready -U signalgrok -d signalgrok
```

### Integration tests inside container network

Run integration tests in the compose network using the test profile:

```bash
docker compose --profile test run --rm integration-tests
```

## Testing

```bash
pytest
```


## Webhook contract (`POST /webhooks/trading-alert`)

Required header:
- `X-SignalGrok-Key`: must match `SIGNALGROK_WEBHOOK_KEY`

Sample payload:

```json
{
  "alert_id": "tv-1001",
  "signal": "SPY MACD Crossover",
  "ticker": "spy",
  "direction": "buy",
  "timeframe": "5m",
  "timestamp": "2025-01-02T03:04:05Z"
}
```

Successful response:

```json
{
  "status": "accepted",
  "ticker": "SPY",
  "signal_type": "SPY_MACD_CROSSOVER",
  "duplicate": false
}
```

Duplicate requests with the same `alert_id` for the configured endpoint are acknowledged with `duplicate: true` and are not inserted twice.
