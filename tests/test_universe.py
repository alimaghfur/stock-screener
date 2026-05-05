"""Unit tests for the ticker universe helpers."""

from __future__ import annotations

from core.universe import (
    DOW30,
    IDX30,
    KOMPAS100,
    LQ45,
    NASDAQ100,
    SP500,
    currency_of,
    get_universe,
    is_idx,
    list_markets,
    list_universes,
    market_of,
)


def test_markets_listed():
    assert "IDX" in list_markets()
    assert "US" in list_markets()


def test_universes_present():
    idx = list_universes("IDX")
    assert "IDX30" in idx
    assert "LQ45" in idx
    assert "IDX80" in idx
    assert "Kompas100" in idx

    us = list_universes("US")
    assert "Large Cap (top ~100)" in us
    assert "Dow 30" in us
    assert "NASDAQ 100" in us
    assert "S&P 500" in us


def test_idx_universe_contains_bbca():
    assert "BBCA.JK" in IDX30
    assert "BBCA.JK" in LQ45
    assert "BBCA.JK" in KOMPAS100


def test_kompas100_size_and_format():
    # ~100 tickers (allowing some flex for delisted-ticker scrubbing).
    assert 90 <= len(KOMPAS100) <= 110
    assert all(t.endswith(".JK") for t in KOMPAS100)


def test_dow30_is_thirty_yahoo_format():
    assert len(DOW30) == 30
    # Dow tickers are bare (no .JK, no class suffix beyond Yahoo dash convention).
    assert all("." not in t for t in DOW30)
    assert "AAPL" in DOW30
    assert "JPM" in DOW30


def test_nasdaq100_size_and_includes_aapl():
    # NASDAQ-100 sometimes has 101 tickers due to dual-class shares.
    assert 100 <= len(NASDAQ100) <= 102
    assert "AAPL" in NASDAQ100
    assert "NVDA" in NASDAQ100


def test_sp500_size_and_includes_brk_b_yahoo_format():
    # S&P 500 has 503 tickers due to three dual-class names.
    assert 500 <= len(SP500) <= 510
    # Yahoo replaces dot with dash for class B shares (BRK.B -> BRK-B).
    assert "BRK-B" in SP500
    assert "BF-B" in SP500
    # No dotted tickers remain.
    assert not any("." in t for t in SP500)


def test_get_universe_returns_list():
    syms = get_universe("US", "Large Cap (top ~100)")
    assert isinstance(syms, list)
    assert "AAPL" in syms


def test_get_universe_for_new_universes():
    assert get_universe("IDX", "Kompas100") == KOMPAS100
    assert get_universe("US", "Dow 30") == DOW30
    assert get_universe("US", "NASDAQ 100") == NASDAQ100
    assert get_universe("US", "S&P 500") == SP500


def test_is_idx_and_currency():
    assert is_idx("BBCA.JK")
    assert not is_idx("AAPL")
    assert currency_of("BBCA.JK") == "IDR"
    assert currency_of("AAPL") == "USD"
    assert market_of("BBRI.JK") == "IDX"
    assert market_of("MSFT") == "US"
