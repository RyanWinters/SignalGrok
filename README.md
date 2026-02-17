# SignalGrok

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# set SIGNALGROK_WEBHOOK_KEY in .env
uvicorn app.main:app --reload
```

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

## API quick test

```bash
curl -X POST http://127.0.0.1:8000/webhooks/trading-alert \
  -H 'Content-Type: application/json' \
  -H 'X-SignalGrok-Key: change-me' \
  -d '{"signal":"SPY MACD Crossover","ticker":"SPY"}'
```
