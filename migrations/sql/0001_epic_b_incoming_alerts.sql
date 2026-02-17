-- Epic B: webhook intake persistence and idempotency
CREATE TABLE IF NOT EXISTS incoming_alerts (
    id VARCHAR(36) PRIMARY KEY,
    webhook_endpoint_id VARCHAR(36) NOT NULL,
    external_alert_id VARCHAR(255),
    raw_payload JSON NOT NULL,
    ticker VARCHAR(16) NOT NULL,
    signal_type VARCHAR(64) NOT NULL,
    direction VARCHAR(16),
    status VARCHAR(32) NOT NULL,
    received_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_incoming_alerts_webhook_endpoint_id
    ON incoming_alerts (webhook_endpoint_id);

CREATE INDEX IF NOT EXISTS ix_incoming_alerts_ticker
    ON incoming_alerts (ticker);

CREATE UNIQUE INDEX IF NOT EXISTS uq_incoming_alerts_endpoint_external
    ON incoming_alerts (webhook_endpoint_id, external_alert_id);
