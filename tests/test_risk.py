"""Unit tests for risk / TP-SL calculations."""

from __future__ import annotations

import pytest

from core.risk import calculate_trade_plan, position_size, unrealized_pnl


def test_long_plan_basics():
    plan = calculate_trade_plan(entry=100.0, atr_value=2.0, side="long", sl_atr_mult=1.5, rr=2.0)
    assert plan.side == "long"
    assert plan.entry == 100.0
    assert plan.stop_loss == pytest.approx(97.0)
    assert plan.tp1 == pytest.approx(103.0)
    assert plan.tp2 == pytest.approx(106.0)
    assert plan.tp3 == pytest.approx(109.0)
    assert plan.risk_per_share == pytest.approx(3.0)


def test_short_plan_basics():
    plan = calculate_trade_plan(entry=100.0, atr_value=2.0, side="short", sl_atr_mult=1.5, rr=2.0)
    assert plan.stop_loss == pytest.approx(103.0)
    assert plan.tp1 == pytest.approx(97.0)
    assert plan.tp2 == pytest.approx(94.0)
    assert plan.tp3 == pytest.approx(91.0)


def test_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_trade_plan(entry=0, atr_value=1, side="long")
    with pytest.raises(ValueError):
        calculate_trade_plan(entry=10, atr_value=0, side="long")
    with pytest.raises(ValueError):
        calculate_trade_plan(entry=10, atr_value=1, side="weird")


def test_position_size():
    out = position_size(account_equity=10_000.0, risk_pct=1.0, entry=100.0, stop_loss=98.0)
    # 1% of 10k = 100 risk; per-share risk = 2 -> qty = 50
    assert out["qty"] == 50
    assert out["risk_amount"] == pytest.approx(100.0)
    assert out["cost"] == pytest.approx(50 * 100.0)


def test_position_size_invalid():
    with pytest.raises(ValueError):
        position_size(account_equity=0, risk_pct=1, entry=100, stop_loss=99)
    with pytest.raises(ValueError):
        position_size(account_equity=1000, risk_pct=0, entry=100, stop_loss=99)
    with pytest.raises(ValueError):
        position_size(account_equity=1000, risk_pct=1, entry=100, stop_loss=100)


def test_unrealized_pnl_long_short():
    long = unrealized_pnl("long", entry=100.0, qty=10, last=110.0)
    assert long["pnl"] == pytest.approx(100.0)
    assert long["pnl_pct"] == pytest.approx(10.0)

    short = unrealized_pnl("short", entry=100.0, qty=10, last=90.0)
    assert short["pnl"] == pytest.approx(100.0)
    assert short["pnl_pct"] == pytest.approx(10.0)
