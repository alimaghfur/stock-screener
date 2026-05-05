"""Technical indicators implemented with pandas/numpy (no external TA library).

All functions accept a Series (close/high/low/volume) and return a Series of the same
length, with NaN for the warm-up window.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False, min_periods=period).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI.

    - When losses are zero and gains > 0 → RSI = 100 (overbought extreme).
    - When gains are zero and losses > 0 → RSI = 0 (oversold extreme).
    - When both are zero (flat) → RSI = 50.
    """
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - (100.0 / (1.0 + rs))
    out = out.where(~((avg_loss == 0) & (avg_gain > 0)), 100.0)
    out = out.where(~((avg_gain == 0) & (avg_loss == 0)), 50.0)
    out = out.where(~((avg_gain == 0) & (avg_loss > 0)), 0.0)
    # Preserve NaNs in the warm-up window.
    return out.where(avg_gain.notna() & avg_loss.notna())


def macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's ATR."""
    tr = true_range(high, low, close)
    return tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    """Session VWAP — resets each calendar day from the index."""
    typical = (high + low + close) / 3.0
    pv = typical * volume
    if not isinstance(close.index, pd.DatetimeIndex):
        cum_pv = pv.cumsum()
        cum_v = volume.cumsum().replace(0.0, np.nan)
        return cum_pv / cum_v
    day = close.index.tz_convert("UTC").date if close.index.tz else close.index.date
    grouper = pd.Index(day, name="day")
    cum_pv = pv.groupby(grouper).cumsum()
    cum_v = volume.groupby(grouper).cumsum().replace(0.0, np.nan)
    return cum_pv / cum_v


def volume_ratio(volume: pd.Series, period: int = 20) -> pd.Series:
    """Current volume / average volume over `period` bars."""
    avg = volume.rolling(window=period, min_periods=period).mean()
    return volume / avg.replace(0.0, np.nan)


def rolling_high(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).max()


def rolling_low(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).min()


def pct_change(series: pd.Series, periods: int = 1) -> pd.Series:
    return series.pct_change(periods=periods) * 100.0
