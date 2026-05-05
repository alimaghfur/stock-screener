"""Unit tests for screener scoring (works on synthetic OHLCV, no network)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.screener import _scalping_score, _swing_score


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
