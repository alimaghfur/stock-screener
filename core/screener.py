"""Screening logic for scalping (intraday) and swing (multi-day) strategies."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from core import indicators as ind
from core.data import fetch_history


@dataclass
class ScreenResult:
    symbol: str
    strategy: str            # "scalping" | "swing" | "bpjs" | "bsjp"
    side: str                # "long" or "short"
    score: float             # 0..100
    last: float
    change_pct: float
    rsi: float
    atr: float
    atr_pct: float
    volume_ratio: float
    reasons: list[str]
    note: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _safe_last(s: pd.Series) -> float:
    s = s.dropna()
    return float(s.iloc[-1]) if not s.empty else float("nan")


def _scalping_score(df: pd.DataFrame) -> ScreenResult | None:
    """Intraday momentum check.

    Long-side filters (must hit at least 3 of 5):
      - last > VWAP
      - RSI(14) between 50 and 75 (momentum, not overbought)
      - last close > rolling-high(20) shifted by 1 (breakout)
      - volume_ratio > 1.5 (volume confirmation)
      - ATR% > 0.4 (enough volatility for scalping)
    """
    if df.empty or len(df) < 30:
        return None

    close = df["Close"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    volume = df["Volume"].astype(float)

    rsi_s = ind.rsi(close, 14)
    atr_s = ind.atr(high, low, close, 14)
    vwap_s = ind.vwap(high, low, close, volume)
    vol_ratio = ind.volume_ratio(volume, 20)
    breakout_level = ind.rolling_high(close, 20).shift(1)

    last = _safe_last(close)
    rsi_v = _safe_last(rsi_s)
    atr_v = _safe_last(atr_s)
    vwap_v = _safe_last(vwap_s)
    vol_v = _safe_last(vol_ratio)
    bo_v = _safe_last(breakout_level)
    if any(pd.isna(x) for x in (last, rsi_v, atr_v, vwap_v, vol_v, bo_v)):
        return None

    atr_pct = (atr_v / last * 100.0) if last else 0.0
    change_pct = float(ind.pct_change(close, 1).iloc[-1]) if len(close) >= 2 else 0.0

    reasons: list[str] = []
    score = 0.0
    if last > vwap_v:
        reasons.append("Above VWAP")
        score += 20
    if 50.0 <= rsi_v <= 75.0:
        reasons.append(f"RSI {rsi_v:.0f} momentum")
        score += 20
    if last >= bo_v:
        reasons.append("20-bar breakout")
        score += 25
    if vol_v >= 1.5:
        reasons.append(f"Vol {vol_v:.1f}x avg")
        score += 20
    if atr_pct >= 0.4:
        reasons.append(f"ATR {atr_pct:.2f}%")
        score += 15

    if len(reasons) < 3:
        return None
    return ScreenResult(
        symbol="",
        strategy="scalping",
        side="long",
        score=round(min(score, 100.0), 1),
        last=round(last, 4),
        change_pct=round(change_pct, 2),
        rsi=round(rsi_v, 1),
        atr=round(atr_v, 4),
        atr_pct=round(atr_pct, 2),
        volume_ratio=round(vol_v, 2),
        reasons=reasons,
    )


def _swing_score(df: pd.DataFrame) -> ScreenResult | None:
    """Multi-day swing trend check.

    Long-side filters (must hit at least 3 of 5):
      - MA20 > MA50 (uptrend)
      - last > MA20
      - RSI(14) between 45 and 65 (healthy, not overbought)
      - MACD histogram positive AND rising
      - volume_ratio >= 1.2
    """
    if df.empty or len(df) < 60:
        return None

    close = df["Close"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    volume = df["Volume"].astype(float)

    ma20 = ind.sma(close, 20)
    ma50 = ind.sma(close, 50)
    rsi_s = ind.rsi(close, 14)
    atr_s = ind.atr(high, low, close, 14)
    _, _, macd_hist = ind.macd(close)
    vol_ratio = ind.volume_ratio(volume, 20)

    last = _safe_last(close)
    ma20_v = _safe_last(ma20)
    ma50_v = _safe_last(ma50)
    rsi_v = _safe_last(rsi_s)
    atr_v = _safe_last(atr_s)
    vol_v = _safe_last(vol_ratio)
    if any(pd.isna(x) for x in (last, ma20_v, ma50_v, rsi_v, atr_v, vol_v)):
        return None

    macd_now = float(macd_hist.iloc[-1]) if not pd.isna(macd_hist.iloc[-1]) else 0.0
    macd_prev = float(macd_hist.iloc[-2]) if len(macd_hist) > 1 else macd_now

    atr_pct = (atr_v / last * 100.0) if last else 0.0
    change_pct = float(ind.pct_change(close, 1).iloc[-1]) if len(close) >= 2 else 0.0

    reasons: list[str] = []
    score = 0.0
    if ma20_v > ma50_v:
        reasons.append("MA20 > MA50")
        score += 25
    if last > ma20_v:
        reasons.append("Above MA20")
        score += 20
    if 45.0 <= rsi_v <= 65.0:
        reasons.append(f"RSI {rsi_v:.0f}")
        score += 15
    if macd_now > 0 and macd_now > macd_prev:
        reasons.append("MACD hist rising")
        score += 25
    if vol_v >= 1.2:
        reasons.append(f"Vol {vol_v:.1f}x avg")
        score += 15

    if len(reasons) < 3:
        return None
    return ScreenResult(
        symbol="",
        strategy="swing",
        side="long",
        score=round(min(score, 100.0), 1),
        last=round(last, 4),
        change_pct=round(change_pct, 2),
        rsi=round(rsi_v, 1),
        atr=round(atr_v, 4),
        atr_pct=round(atr_pct, 2),
        volume_ratio=round(vol_v, 2),
        reasons=reasons,
    )


# ---------------------------------------------------------------------------
# Indonesian intraday / overnight pattern strategies
# ---------------------------------------------------------------------------

# Lookback for the BPJS / BSJP edge calculation.
_PATTERN_LOOKBACK = 20

# Filters: minimum positive edge and minimum consistency (% of green days).
_BPJS_MIN_EDGE = 0.003   # 0.30 % average intraday return
_BPJS_MIN_GREEN = 0.60   # at least 12/20 days closed > opened
_BSJP_MIN_EDGE = 0.002   # 0.20 % average overnight gap
_BSJP_MIN_GREEN = 0.55   # at least 11/20 days gapped up

# Score-cap reference points (where the edge contributes the full 50 pts).
_BPJS_EDGE_CAP = 0.015   # 1.5 % avg intraday return = full edge score
_BSJP_EDGE_CAP = 0.010   # 1.0 % avg overnight gap = full edge score


def _bpjs_score(df: pd.DataFrame) -> ScreenResult | None:
    """Beli Pagi Jual Sore — buy at open, sell at close (intraday).

    Long-only filter, looks for stocks whose Open→Close return tends to be
    positive over the last `_PATTERN_LOOKBACK` daily bars:
      - avg intraday return ((Close − Open) / Open) ≥ ``_BPJS_MIN_EDGE``
      - green-day ratio (Close > Open) ≥ ``_BPJS_MIN_GREEN``

    The score combines edge size and consistency (50 / 50).
    """
    if df.empty or len(df) < _PATTERN_LOOKBACK + 14:
        return None

    close = df["Close"].astype(float)
    open_ = df["Open"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    volume = df["Volume"].astype(float)

    intraday_ret = ((close - open_) / open_).iloc[-_PATTERN_LOOKBACK:].dropna()
    if len(intraday_ret) < _PATTERN_LOOKBACK:
        return None
    avg_edge = float(intraday_ret.mean())
    green_days = int((intraday_ret > 0).sum())
    green_ratio = green_days / _PATTERN_LOOKBACK

    if avg_edge < _BPJS_MIN_EDGE or green_ratio < _BPJS_MIN_GREEN:
        return None

    rsi_v = _safe_last(ind.rsi(close, 14))
    atr_v = _safe_last(ind.atr(high, low, close, 14))
    vol_v = _safe_last(ind.volume_ratio(volume, 20))
    last = _safe_last(close)
    if any(pd.isna(x) for x in (last, rsi_v, atr_v, vol_v)):
        return None

    atr_pct = (atr_v / last * 100.0) if last else 0.0
    change_pct = float(ind.pct_change(close, 1).iloc[-1]) if len(close) >= 2 else 0.0

    reasons = [
        f"Avg O→C +{avg_edge * 100:.2f}% (20d)",
        f"{green_days}/{_PATTERN_LOOKBACK} green days",
    ]
    if vol_v >= 1.2:
        reasons.append(f"Vol {vol_v:.1f}x avg")

    edge_score = min(avg_edge / _BPJS_EDGE_CAP, 1.0) * 50.0
    cons_score = ((green_ratio - _BPJS_MIN_GREEN) / (1.0 - _BPJS_MIN_GREEN)) * 50.0
    cons_score = max(0.0, min(cons_score, 50.0))
    score = round(edge_score + cons_score, 1)

    return ScreenResult(
        symbol="",
        strategy="bpjs",
        side="long",
        score=score,
        last=round(last, 4),
        change_pct=round(change_pct, 2),
        rsi=round(rsi_v, 1),
        atr=round(atr_v, 4),
        atr_pct=round(atr_pct, 2),
        volume_ratio=round(vol_v, 2),
        reasons=reasons,
    )


def _bsjp_score(df: pd.DataFrame) -> ScreenResult | None:
    """Beli Sore Jual Pagi — buy at close, sell at next open (overnight).

    Long-only filter, looks for stocks whose overnight gap tends to be
    positive over the last `_PATTERN_LOOKBACK` daily bars:
      - avg overnight gap ((Open − prev Close) / prev Close) ≥ ``_BSJP_MIN_EDGE``
      - gap-up ratio (Open > prev Close) ≥ ``_BSJP_MIN_GREEN``
    """
    if df.empty or len(df) < _PATTERN_LOOKBACK + 14:
        return None

    close = df["Close"].astype(float)
    open_ = df["Open"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    volume = df["Volume"].astype(float)

    prev_close = close.shift(1)
    overnight = ((open_ - prev_close) / prev_close).iloc[-_PATTERN_LOOKBACK:].dropna()
    if len(overnight) < _PATTERN_LOOKBACK:
        return None
    avg_gap = float(overnight.mean())
    gap_up_days = int((overnight > 0).sum())
    gap_up_ratio = gap_up_days / _PATTERN_LOOKBACK

    if avg_gap < _BSJP_MIN_EDGE or gap_up_ratio < _BSJP_MIN_GREEN:
        return None

    rsi_v = _safe_last(ind.rsi(close, 14))
    atr_v = _safe_last(ind.atr(high, low, close, 14))
    vol_v = _safe_last(ind.volume_ratio(volume, 20))
    last = _safe_last(close)
    if any(pd.isna(x) for x in (last, rsi_v, atr_v, vol_v)):
        return None

    atr_pct = (atr_v / last * 100.0) if last else 0.0
    change_pct = float(ind.pct_change(close, 1).iloc[-1]) if len(close) >= 2 else 0.0

    reasons = [
        f"Avg overnight gap +{avg_gap * 100:.2f}% (20d)",
        f"{gap_up_days}/{_PATTERN_LOOKBACK} gap-up days",
    ]
    if vol_v >= 1.2:
        reasons.append(f"Vol {vol_v:.1f}x avg")

    edge_score = min(avg_gap / _BSJP_EDGE_CAP, 1.0) * 50.0
    cons_score = ((gap_up_ratio - _BSJP_MIN_GREEN) / (1.0 - _BSJP_MIN_GREEN)) * 50.0
    cons_score = max(0.0, min(cons_score, 50.0))
    score = round(edge_score + cons_score, 1)

    return ScreenResult(
        symbol="",
        strategy="bsjp",
        side="long",
        score=score,
        last=round(last, 4),
        change_pct=round(change_pct, 2),
        rsi=round(rsi_v, 1),
        atr=round(atr_v, 4),
        atr_pct=round(atr_pct, 2),
        volume_ratio=round(vol_v, 2),
        reasons=reasons,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Strategies that are only meaningful on Indonesian equities (sesi pagi/sore).
IDX_ONLY_STRATEGIES = ("bpjs", "bsjp")


def strategies_for_market(market: str) -> list[str]:
    """Return the list of strategies available for the given market."""
    base = ["scalping", "swing"]
    if market.upper() == "IDX":
        return base + list(IDX_ONLY_STRATEGIES)
    return base


def screen_symbol(symbol: str, strategy: str) -> ScreenResult | None:
    """Screen a single symbol; returns None if it doesn't qualify."""
    if strategy == "scalping":
        df = fetch_history(symbol, period="60d", interval="15m")
        if df.empty or len(df) < 30:
            df = fetch_history(symbol, period="3mo", interval="60m")
        result = _scalping_score(df)
    elif strategy == "swing":
        df = fetch_history(symbol, period="6mo", interval="1d")
        result = _swing_score(df)
    elif strategy == "bpjs":
        df = fetch_history(symbol, period="6mo", interval="1d")
        result = _bpjs_score(df)
    elif strategy == "bsjp":
        df = fetch_history(symbol, period="6mo", interval="1d")
        result = _bsjp_score(df)
    else:
        raise ValueError(f"unknown strategy: {strategy}")
    if result is not None:
        result.symbol = symbol
    return result


def screen_universe(symbols: list[str], strategy: str) -> list[ScreenResult]:
    """Screen many symbols and return only those that qualify, sorted by score desc."""
    results: list[ScreenResult] = []
    for sym in symbols:
        try:
            r = screen_symbol(sym, strategy)
        except Exception:
            r = None
        if r is not None:
            results.append(r)
    results.sort(key=lambda x: x.score, reverse=True)
    return results


def top_movers(symbols: list[str], top_n: int = 10) -> tuple[list[dict], list[dict]]:
    """Return (gainers, losers) computed from latest daily close vs previous close."""
    from core.data import quotes_table

    df = quotes_table(symbols, period="5d")
    if df.empty:
        return [], []
    df = df.dropna(subset=["Change %"]).sort_values("Change %", ascending=False)
    gainers = df.head(top_n).to_dict(orient="records")
    losers = df.tail(top_n).iloc[::-1].to_dict(orient="records")
    return gainers, losers
