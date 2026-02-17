"""Alert service helpers."""


def normalize_ticker(raw_ticker: str) -> str:
    return raw_ticker.upper().strip()
