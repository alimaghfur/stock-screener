"""Data layer — fetches OHLCV data from Yahoo Finance via yfinance.

Wrapped behind small helper functions so a real-time provider can be plugged in later
without changes to the screener / UI code.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

# Streamlit may not be installed in plain test environments; cache decorator is a no-op
# fallback so the module still imports cleanly.
try:  # pragma: no cover - exercised at runtime
    import streamlit as st

    def _cache_data(*args: Any, **kwargs: Any):
        return st.cache_data(*args, **kwargs)
except Exception:  # pragma: no cover
    def _cache_data(*args: Any, **kwargs: Any):
        def deco(fn):
            return fn
        return deco


def _yfinance():
    """Lazy-import yfinance so unit tests don't require network/library at import time."""
    import yfinance as yf
    return yf


# --- Single ticker history -----------------------------------------------------------

@_cache_data(ttl=300, show_spinner=False)
def fetch_history(
    symbol: str,
    period: str = "6mo",
    interval: str = "1d",
) -> pd.DataFrame:
    """Return OHLCV history for a single symbol. Empty DataFrame on failure."""
    yf = _yfinance()
    try:
        df = yf.download(
            tickers=symbol,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            threads=False,
        )
    except Exception:
        return pd.DataFrame()
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.title)  # Open/High/Low/Close/Volume
    keep = [c for c in ("Open", "High", "Low", "Close", "Volume") if c in df.columns]
    df = df[keep].dropna(how="all")
    return df


# --- Batch fetcher (used by Top Movers / Screener) -----------------------------------

@_cache_data(ttl=300, show_spinner=False)
def fetch_history_batch(
    symbols: tuple[str, ...],
    period: str = "5d",
    interval: str = "1d",
) -> dict[str, pd.DataFrame]:
    """Fetch OHLCV for many symbols in one call. Returns {symbol: DataFrame}."""
    if not symbols:
        return {}
    yf = _yfinance()
    try:
        df = yf.download(
            tickers=list(symbols),
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
            group_by="ticker",
            threads=True,
        )
    except Exception:
        return {}
    if df is None or df.empty:
        return {}

    out: dict[str, pd.DataFrame] = {}
    if isinstance(df.columns, pd.MultiIndex):
        for sym in symbols:
            if sym in df.columns.get_level_values(0):
                sub = df[sym].dropna(how="all")
                sub = sub.rename(columns=str.title)
                if not sub.empty:
                    out[sym] = sub
    else:
        sym = symbols[0]
        sub = df.rename(columns=str.title).dropna(how="all")
        if not sub.empty:
            out[sym] = sub
    return out


# --- Latest quote (price + change %) -------------------------------------------------

@_cache_data(ttl=60, show_spinner=False)
def fetch_quote(symbol: str) -> dict:
    """Return {price, prev_close, change, change_pct, currency, name} or empty dict."""
    df = fetch_history(symbol, period="5d", interval="1d")
    if df.empty or "Close" not in df.columns or len(df) < 2:
        return {}
    last = float(df["Close"].iloc[-1])
    prev = float(df["Close"].iloc[-2])
    change = last - prev
    pct = (change / prev * 100.0) if prev else 0.0
    return {
        "symbol": symbol,
        "price": last,
        "prev_close": prev,
        "change": change,
        "change_pct": pct,
    }


def quotes_table(symbols: list[str], period: str = "5d") -> pd.DataFrame:
    """Build a quote table for a list of symbols using a single batched call."""
    if not symbols:
        return pd.DataFrame(
            columns=["Symbol", "Last", "Prev Close", "Change", "Change %", "Volume"]
        )
    batch = fetch_history_batch(tuple(symbols), period=period, interval="1d")
    rows: list[dict] = []
    for sym in symbols:
        df = batch.get(sym)
        if df is None or df.empty or len(df) < 2 or "Close" not in df.columns:
            continue
        last = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])
        vol = float(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0.0
        change = last - prev
        pct = (change / prev * 100.0) if prev else 0.0
        rows.append({
            "Symbol": sym,
            "Last": last,
            "Prev Close": prev,
            "Change": change,
            "Change %": pct,
            "Volume": vol,
        })
    return pd.DataFrame(rows)


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()
