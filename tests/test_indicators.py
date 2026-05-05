"""Unit tests for technical indicators."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from core import indicators as ind


def _make_ohlcv(n: int = 120, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    drift = np.linspace(100, 130, n)
    noise = rng.normal(0, 1.0, n)
    close = drift + noise
    high = close + rng.uniform(0.1, 1.0, n)
    low = close - rng.uniform(0.1, 1.0, n)
    open_ = np.concatenate([[close[0]], close[:-1]])
    volume = rng.integers(1_000, 10_000, n).astype(float)
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=idx,
    )


def test_sma_matches_pandas_rolling_mean():
    df = _make_ohlcv()
    out = ind.sma(df["Close"], 10)
    expected = df["Close"].rolling(10, min_periods=10).mean()
    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_ema_finite_after_warmup():
    df = _make_ohlcv()
    out = ind.ema(df["Close"], 12)
    assert out.iloc[:11].isna().all()
    assert np.isfinite(out.iloc[12:]).all()


def test_rsi_in_bounds():
    df = _make_ohlcv()
    rsi_v = ind.rsi(df["Close"], 14).dropna()
    assert (rsi_v >= 0).all() and (rsi_v <= 100).all()


def test_rsi_extremes():
    up = pd.Series(np.arange(1, 50, dtype=float))
    down = pd.Series(np.arange(50, 1, -1, dtype=float))
    assert ind.rsi(up, 14).iloc[-1] > 90
    assert ind.rsi(down, 14).iloc[-1] < 10


def test_macd_zero_for_constant_series():
    s = pd.Series([10.0] * 200)
    m, sig, hist = ind.macd(s)
    assert abs(m.dropna().iloc[-1]) < 1e-9
    assert abs(hist.dropna().iloc[-1]) < 1e-9


def test_atr_positive():
    df = _make_ohlcv()
    a = ind.atr(df["High"], df["Low"], df["Close"], 14).dropna()
    assert (a > 0).all()


def test_vwap_between_low_and_high():
    df = _make_ohlcv()
    v = ind.vwap(df["High"], df["Low"], df["Close"], df["Volume"]).dropna()
    assert (v >= df["Low"].min() - 1e-6).all()
    assert (v <= df["High"].max() + 1e-6).all()


def test_volume_ratio_around_one_when_constant_volume():
    s = pd.Series([1000.0] * 60)
    out = ind.volume_ratio(s, 20).dropna()
    assert pytest.approx(out.iloc[-1], rel=1e-9) == 1.0
