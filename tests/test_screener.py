"""Unit tests for screener scoring (works on synthetic OHLCV, no network)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.screener import (
    IDX_ONLY_STRATEGIES,
    _bpjs_score,
    _bsjp_score,
    _scalping_score,
    _swing_score,
    strategies_for_market,
)


def _trending_up(n: int = 250, start: float = 100.0, drift: float = 0.5, noise: float = 0.2) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    close = start + np.arange(n) * drift + rng.normal(0, noise, n)
    high = close + rng.uniform(0.05, 0.4, n)
    low = close - rng.uniform(0.05, 0.4, n)
    open_ = np.concatenate([[close[0]], close[:-1]])
    volume = rng.uniform(1500, 2500, n)
    # Spike volume on the last bar so volume_ratio passes.
    volume[-1] = float(np.mean(volume[-30:])) * 3.0
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )


def _flat(n: int = 250, value: float = 100.0) -> pd.DataFrame:
    close = np.full(n, value)
    high = close + 0.01
    low = close - 0.01
    open_ = close
    volume = np.full(n, 1000.0)
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )


def test_swing_score_passes_on_uptrend():
    df = _trending_up()
    r = _swing_score(df)
    assert r is not None
    assert r.strategy == "swing"
    assert r.side == "long"
    assert r.score > 0
    assert any("MA20 > MA50" in reason for reason in r.reasons)


def test_swing_score_rejects_flat():
    df = _flat()
    r = _swing_score(df)
    assert r is None


def test_scalping_score_handles_short_history():
    df = _flat(n=10)
    r = _scalping_score(df)
    assert r is None


# ---------------------------------------------------------------------------
# BPJS (Beli Pagi Jual Sore) — buy at open, sell at close
# ---------------------------------------------------------------------------

def _intraday_bullish(n: int = 60, base: float = 100.0, edge_pct: float = 0.6) -> pd.DataFrame:
    """OHLCV where Close consistently > Open by ~edge_pct% (intraday bullish)."""
    rng = np.random.default_rng(7)
    open_ = base + rng.normal(0, 0.05, n)
    close = open_ * (1.0 + edge_pct / 100.0 + rng.normal(0, 0.0005, n))
    high = np.maximum(open_, close) + rng.uniform(0.05, 0.2, n)
    low = np.minimum(open_, close) - rng.uniform(0.05, 0.2, n)
    volume = rng.uniform(1500, 2500, n)
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )


def _intraday_bearish(n: int = 60, base: float = 100.0, edge_pct: float = -0.6) -> pd.DataFrame:
    """OHLCV where Close consistently < Open (intraday bearish)."""
    return _intraday_bullish(n=n, base=base, edge_pct=edge_pct)


def test_bpjs_score_passes_on_intraday_bullish():
    df = _intraday_bullish()
    r = _bpjs_score(df)
    assert r is not None
    assert r.strategy == "bpjs"
    assert r.side == "long"
    assert 0.0 < r.score <= 100.0
    # Reason should report the green-day count and edge.
    assert any("green days" in reason for reason in r.reasons)
    assert any("Avg O→C" in reason for reason in r.reasons)


def test_bpjs_score_rejects_intraday_bearish():
    df = _intraday_bearish()
    r = _bpjs_score(df)
    assert r is None


def test_bpjs_score_rejects_flat_or_short():
    assert _bpjs_score(_flat()) is None
    assert _bpjs_score(_flat(n=10)) is None


def test_bpjs_score_rejects_marginal_edge_low_consistency():
    """Edge passes the 0.3 % threshold but only ~50 % green days → should reject."""
    rng = np.random.default_rng(11)
    n = 60
    open_ = 100.0 + rng.normal(0, 0.05, n)
    # Half the days are big winners (+1 %), the other half are small losers (-0.4 %).
    pattern = np.where(rng.random(n) > 0.5, 0.010, -0.004)
    close = open_ * (1.0 + pattern)
    high = np.maximum(open_, close) + 0.1
    low = np.minimum(open_, close) - 0.1
    volume = np.full(n, 2000.0)
    df = pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=pd.date_range("2024-01-01", periods=n, freq="D"),
    )
    r = _bpjs_score(df)
    # Even if avg edge ≥ 0.3 %, green-day ratio is ~50 % which is below the 60 % floor.
    assert r is None


# ---------------------------------------------------------------------------
# BSJP (Beli Sore Jual Pagi) — buy at close, sell at next open
# ---------------------------------------------------------------------------

def _overnight_gap_up(n: int = 60, base: float = 100.0, gap_pct: float = 0.4) -> pd.DataFrame:
    """OHLCV where each Open opens ~gap_pct% above the previous Close."""
    rng = np.random.default_rng(13)
    closes = [base]
    opens = [base]
    for _ in range(1, n):
        prev_close = closes[-1]
        nxt_open = prev_close * (1.0 + gap_pct / 100.0 + rng.normal(0, 0.0005))
        nxt_close = nxt_open + rng.normal(0, 0.05)
        opens.append(nxt_open)
        closes.append(nxt_close)
    open_ = np.array(opens)
    close = np.array(closes)
    high = np.maximum(open_, close) + rng.uniform(0.05, 0.2, n)
    low = np.minimum(open_, close) - rng.uniform(0.05, 0.2, n)
    volume = rng.uniform(1500, 2500, n)
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )


def test_bsjp_score_passes_on_consistent_gap_up():
    df = _overnight_gap_up()
    r = _bsjp_score(df)
    assert r is not None
    assert r.strategy == "bsjp"
    assert r.side == "long"
    assert 0.0 < r.score <= 100.0
    assert any("gap-up days" in reason for reason in r.reasons)
    assert any("Avg overnight gap" in reason for reason in r.reasons)


def test_bsjp_score_rejects_consistent_gap_down():
    df = _overnight_gap_up(gap_pct=-0.4)
    r = _bsjp_score(df)
    assert r is None


def test_bsjp_score_rejects_flat_or_short():
    assert _bsjp_score(_flat()) is None
    assert _bsjp_score(_flat(n=10)) is None


# ---------------------------------------------------------------------------
# Strategy availability per market
# ---------------------------------------------------------------------------

def test_strategies_for_market_idx_includes_bpjs_bsjp():
    strategies = strategies_for_market("IDX")
    assert "scalping" in strategies
    assert "swing" in strategies
    assert "bpjs" in strategies
    assert "bsjp" in strategies


def test_strategies_for_market_us_excludes_bpjs_bsjp():
    strategies = strategies_for_market("US")
    assert "scalping" in strategies
    assert "swing" in strategies
    for s in IDX_ONLY_STRATEGIES:
        assert s not in strategies
