"""Risk management: ATR-based TP/SL suggestion and position sizing."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class TradePlan:
    side: str            # "long" or "short"
    entry: float
    stop_loss: float
    tp1: float           # 1R
    tp2: float           # 2R (default risk:reward target)
    tp3: float           # 3R
    risk_per_share: float
    risk_reward: float   # the rr used for tp2
    atr: float

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_trade_plan(
    entry: float,
    atr_value: float,
    side: str = "long",
    sl_atr_mult: float = 1.5,
    rr: float = 2.0,
) -> TradePlan:
    """Build a TradePlan from entry price, ATR, side, and risk params.

    - SL = entry -/+ sl_atr_mult * ATR (depending on side)
    - TP1 / TP2 / TP3 = entry +/- (1R, rr*R, (rr+1)*R) where R = sl_atr_mult * ATR
    """
    if entry <= 0:
        raise ValueError("entry must be positive")
    if atr_value <= 0:
        raise ValueError("atr must be positive")
    if side not in ("long", "short"):
        raise ValueError("side must be 'long' or 'short'")
    if sl_atr_mult <= 0:
        raise ValueError("sl_atr_mult must be positive")
    if rr <= 0:
        raise ValueError("rr must be positive")

    risk = sl_atr_mult * atr_value
    if side == "long":
        sl = entry - risk
        tp1 = entry + risk
        tp2 = entry + rr * risk
        tp3 = entry + (rr + 1.0) * risk
    else:
        sl = entry + risk
        tp1 = entry - risk
        tp2 = entry - rr * risk
        tp3 = entry - (rr + 1.0) * risk

    return TradePlan(
        side=side,
        entry=round(entry, 4),
        stop_loss=round(sl, 4),
        tp1=round(tp1, 4),
        tp2=round(tp2, 4),
        tp3=round(tp3, 4),
        risk_per_share=round(risk, 4),
        risk_reward=rr,
        atr=round(atr_value, 4),
    )


def position_size(
    account_equity: float,
    risk_pct: float,
    entry: float,
    stop_loss: float,
) -> dict:
    """How many shares to buy so that loss at SL = risk_pct% of account."""
    if account_equity <= 0:
        raise ValueError("account_equity must be positive")
    if not (0.0 < risk_pct <= 100.0):
        raise ValueError("risk_pct must be in (0, 100]")
    risk_per_share = abs(entry - stop_loss)
    if risk_per_share <= 0:
        raise ValueError("entry and stop_loss must differ")

    risk_amount = account_equity * (risk_pct / 100.0)
    qty = risk_amount / risk_per_share
    cost = qty * entry
    return {
        "risk_amount": round(risk_amount, 2),
        "risk_per_share": round(risk_per_share, 4),
        "qty": int(qty),  # whole shares
        "qty_raw": round(qty, 4),
        "cost": round(cost, 2),
    }


def unrealized_pnl(side: str, entry: float, qty: float, last: float) -> dict:
    """Compute unrealized P/L for an open position."""
    pnl = (last - entry) * qty if side == "long" else (entry - last) * qty
    cost = entry * qty
    pct = (pnl / cost * 100.0) if cost else 0.0
    return {"pnl": round(pnl, 2), "pnl_pct": round(pct, 2)}
