"""Unit tests for the ticker universe helpers."""

from __future__ import annotations

from core.universe import (
    IDX30,
    LQ45,
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
    assert "IDX30" in list_universes("IDX")
    assert "LQ45" in list_universes("IDX")
    assert "Large Cap (top ~100)" in list_universes("US")


def test_idx_universe_contains_bbca():
    assert "BBCA.JK" in IDX30
    assert "BBCA.JK" in LQ45


def test_get_universe_returns_list():
    syms = get_universe("US", "Large Cap (top ~100)")
    assert isinstance(syms, list)
    assert "AAPL" in syms


def test_is_idx_and_currency():
    assert is_idx("BBCA.JK")
    assert not is_idx("AAPL")
    assert currency_of("BBCA.JK") == "IDR"
    assert currency_of("AAPL") == "USD"
    assert market_of("BBRI.JK") == "IDX"
    assert market_of("MSFT") == "US"
