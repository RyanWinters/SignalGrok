# SignalGrok

SignalGrok ingests trading alerts via webhook and normalizes them for downstream processing.

## Local development

```bash
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```
