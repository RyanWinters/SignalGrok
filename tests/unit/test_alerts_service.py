from app.services.alerts import normalize_ticker


def test_normalize_ticker() -> None:
    assert normalize_ticker(" spy ") == "SPY"
