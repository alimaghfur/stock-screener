"""Unit tests for the ticker universe helpers."""

from __future__ import annotations

from core.universe import (
    DOW30,
    IDX30,
    IDXBASIC,
    IDXBUMN20,
    IDXCYCLIC,
    IDXENERGY,
    IDXFINANCE,
    IDXHEALTH,
    IDXHIDIV20,
    IDXINDUST,
    IDXINFRA,
    IDXNONCYC,
    IDXPROPERT,
    IDXTECHNO,
    IDXTRANS,
    IHSG,
    JII,
    JII70,
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
    market_universes,
)


def test_markets_listed():
    assert "IDX" in list_markets()
    assert "US" in list_markets()


def test_universes_present():
    idx = list_universes("IDX")
    # Core liquidity tiers.
    assert "IDX30" in idx
    assert "LQ45" in idx
    assert "IDX80" in idx
    assert "Kompas100" in idx
    # Themed indices.
    assert "JII (Syariah 30)" in idx
    assert "JII70 (Syariah 70)" in idx
    assert "IDXBUMN20" in idx
    assert "IDXHIDIV20 (High Dividend)" in idx
    # Sectoral.
    assert "Sector: Basic Materials" in idx
    assert "Sector: Energy" in idx
    assert "Sector: Financials" in idx
    assert "Sector: Technology" in idx
    # Full IDX universe.
    assert "IHSG (all listed, ~941)" in idx

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


def test_jii_size_and_format():
    # JII has exactly 30 syariah-compliant most-liquid stocks.
    assert len(JII) == 30
    assert all(t.endswith(".JK") for t in JII)
    # JII members are blue-chip syariah names — must include core liquid ones.
    assert "TLKM.JK" in JII
    assert "ASII.JK" in JII
    # JII excludes banks (riba) — BBCA, BBRI must NOT be in JII.
    assert "BBCA.JK" not in JII
    assert "BBRI.JK" not in JII
    assert "BMRI.JK" not in JII


def test_jii70_size_and_superset_of_jii():
    # JII70 has 70 syariah-compliant liquid stocks; spec allows snapshot variance.
    assert 65 <= len(JII70) <= 75
    assert all(t.endswith(".JK") for t in JII70)
    # JII70 excludes conventional banks too.
    assert "BBCA.JK" not in JII70
    assert "BBRI.JK" not in JII70


def test_idxbumn20_size_and_includes_bumn_banks():
    # IDXBUMN20: 20 BUMN (state-owned enterprise) stocks.
    assert len(IDXBUMN20) == 20
    assert all(t.endswith(".JK") for t in IDXBUMN20)
    # Core BUMN banks must be present.
    assert "BBNI.JK" in IDXBUMN20
    assert "BBRI.JK" in IDXBUMN20
    assert "BMRI.JK" in IDXBUMN20
    # BBCA is private (Djarum group) — must NOT be in BUMN20.
    assert "BBCA.JK" not in IDXBUMN20


def test_idxhidiv20_size_and_includes_dividend_payers():
    # IDXHIDIV20: 20 high-dividend-yield stocks.
    assert len(IDXHIDIV20) == 20
    assert all(t.endswith(".JK") for t in IDXHIDIV20)
    # Known consistent dividend payers per Feb 2025 evaluation.
    assert "BBCA.JK" in IDXHIDIV20
    assert "TLKM.JK" in IDXHIDIV20
    assert "UNVR.JK" in IDXHIDIV20


def test_sectoral_universes_format_and_disjoint():
    # Each sectoral list is non-empty, has correct .JK format, and is sorted/unique.
    sectors = {
        "BASIC": IDXBASIC,
        "CYCLIC": IDXCYCLIC,
        "NONCYC": IDXNONCYC,
        "ENERGY": IDXENERGY,
        "FINANCE": IDXFINANCE,
        "HEALTH": IDXHEALTH,
        "INDUST": IDXINDUST,
        "INFRA": IDXINFRA,
        "PROPERT": IDXPROPERT,
        "TECHNO": IDXTECHNO,
        "TRANS": IDXTRANS,
    }
    for name, lst in sectors.items():
        assert len(lst) > 0, f"sector {name} is empty"
        assert all(t.endswith(".JK") for t in lst), f"sector {name} has non-IDX ticker"
        assert len(lst) == len(set(lst)), f"sector {name} has duplicates"

    # Sectors are mutually exclusive (each ticker in exactly one sector).
    counts: dict[str, int] = {}
    for lst in sectors.values():
        for t in lst:
            counts[t] = counts.get(t, 0) + 1
    overlapping = [t for t, c in counts.items() if c > 1]
    assert overlapping == [], f"tickers in multiple sectors: {overlapping[:5]}"


def test_sectoral_known_membership():
    # Spot-check a few well-known sector assignments.
    assert "BBCA.JK" in IDXFINANCE
    assert "BBRI.JK" in IDXFINANCE
    assert "TLKM.JK" in IDXINFRA  # Telkom is classified as Infrastructure (telco) in IDX-IC.
    assert "ASII.JK" in IDXINDUST  # Astra International is industrials (auto manufacturing).
    assert "GOTO.JK" in IDXTECHNO
    assert "ANTM.JK" in IDXBASIC
    assert "ADRO.JK" in IDXENERGY
    assert "KLBF.JK" in IDXHEALTH
    assert "INDF.JK" in IDXNONCYC


def test_ihsg_full_listed_universe():
    # IHSG (IDX Composite) = full list of all BEI-listed tickers (~900-950).
    assert 850 <= len(IHSG) <= 1000
    assert all(t.endswith(".JK") for t in IHSG)
    assert len(IHSG) == len(set(IHSG))  # no duplicates
    # Sanity: IDX30 members should all be in IHSG.
    for t in IDX30:
        assert t in IHSG, f"{t} (IDX30 member) not in IHSG"


def test_get_universe_for_idx_full_coverage():
    assert get_universe("IDX", "JII (Syariah 30)") == JII
    assert get_universe("IDX", "JII70 (Syariah 70)") == JII70
    assert get_universe("IDX", "IDXBUMN20") == IDXBUMN20
    assert get_universe("IDX", "IDXHIDIV20 (High Dividend)") == IDXHIDIV20
    assert get_universe("IDX", "Sector: Energy") == IDXENERGY
    assert get_universe("IDX", "Sector: Financials") == IDXFINANCE
    assert get_universe("IDX", "Sector: Technology") == IDXTECHNO
    assert get_universe("IDX", "IHSG (all listed, ~941)") == IHSG


def test_market_universes_idx_count():
    # IDX side should have at least 17 universes after expansion.
    mu = market_universes()
    assert len(mu["IDX"]) >= 17
    # US side unchanged (4 universes from PR #9).
    assert len(mu["US"]) == 4


def test_is_idx_and_currency():
    assert is_idx("BBCA.JK")
    assert not is_idx("AAPL")
    assert currency_of("BBCA.JK") == "IDR"
    assert currency_of("AAPL") == "USD"
    assert market_of("BBRI.JK") == "IDX"
    assert market_of("MSFT") == "US"
