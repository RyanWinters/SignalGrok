# Migrations

SQL migration scripts live in `migrations/sql`.

Apply the Epic B migration manually with psql:

```bash
psql "$DATABASE_URL" -f migrations/sql/0001_epic_b_incoming_alerts.sql
```

This migration creates the `incoming_alerts` table plus indexes and the idempotency unique index on `(webhook_endpoint_id, external_alert_id)`.
