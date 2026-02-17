"""Finnhub HTTP client."""

from __future__ import annotations

import logging
import random
import time
from datetime import date

import httpx

from app.schemas.news import RawNewsItem

logger = logging.getLogger(__name__)


class FinnhubError(Exception):
    """Base error for Finnhub client failures."""


class FinnhubTransientError(FinnhubError):
    """Raised when a retryable error persists beyond max attempts."""


class FinnhubPermanentError(FinnhubError):
    """Raised for non-retryable Finnhub API failures."""


class FinnhubClient:
    """Client wrapper for Finnhub company-news endpoint."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://finnhub.io/api/v1",
        timeout_seconds: float = 10.0,
        max_attempts: int = 3,
        backoff_base_seconds: float = 0.25,
        backoff_max_seconds: float = 5.0,
        backoff_jitter_seconds: float = 0.2,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout_seconds)
        self._max_attempts = max_attempts
        self._backoff_base_seconds = max(0.0, backoff_base_seconds)
        self._backoff_max_seconds = max(self._backoff_base_seconds, backoff_max_seconds)
        self._backoff_jitter_seconds = max(0.0, backoff_jitter_seconds)

    def fetch_company_news(
        self,
        ticker: str,
        from_date: date,
        to_date: date,
    ) -> list[RawNewsItem]:
        """Fetch company news from Finnhub and parse into typed items."""
        endpoint = "/company-news"
        params = {
            "symbol": ticker,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "token": self._api_key,
        }

        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                with httpx.Client(base_url=self._base_url, timeout=self._timeout) as client:
                    response = client.get(endpoint, params=params)

                if self._is_retryable_status(response.status_code):
                    raise FinnhubTransientError(
                        f"Finnhub retryable status code: {response.status_code}"
                    )

                if 400 <= response.status_code < 500:
                    raise FinnhubPermanentError(
                        f"Finnhub request rejected with status {response.status_code}"
                    )

                response.raise_for_status()
                payload = response.json()
                return [RawNewsItem.model_validate(item) for item in payload]

            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                last_error = exc
                retryable = True
            except FinnhubTransientError as exc:
                last_error = exc
                retryable = True
            except httpx.HTTPStatusError as exc:
                last_error = exc
                retryable = self._is_retryable_status(exc.response.status_code)
                if not retryable:
                    raise FinnhubPermanentError(
                        f"Finnhub HTTP error {exc.response.status_code}"
                    ) from exc
            except (httpx.HTTPError, ValueError) as exc:
                # Covers request errors and malformed JSON payloads.
                last_error = exc
                retryable = True

            if not retryable:
                break

            if attempt < self._max_attempts:
                backoff_seconds = self._compute_backoff_seconds(attempt)
                logger.warning(
                    "Retrying Finnhub request",
                    extra={
                        "attempt": attempt,
                        "max_attempts": self._max_attempts,
                        "backoff_seconds": round(backoff_seconds, 3),
                        "ticker": ticker,
                    },
                )
                time.sleep(backoff_seconds)

        raise FinnhubTransientError("Finnhub request failed after max retry attempts") from last_error

    def _compute_backoff_seconds(self, attempt: int) -> float:
        exp_backoff = min(self._backoff_base_seconds * (2 ** (attempt - 1)), self._backoff_max_seconds)
        jitter = random.uniform(0.0, self._backoff_jitter_seconds)
        return min(exp_backoff + jitter, self._backoff_max_seconds)

    @staticmethod
    def _is_retryable_status(status_code: int) -> bool:
        return status_code == 429 or 500 <= status_code < 600
