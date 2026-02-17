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
