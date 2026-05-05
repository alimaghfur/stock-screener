"""Screener page — scalping & swing scans with TP/SL suggestion."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.data import fetch_history, fetch_quote, normalize_symbol
from core.indicators import atr
from core.risk import calculate_trade_plan, position_size
from core.screener import screen_universe
from core.universe import (
    currency_of,
    get_universe,
    list_markets,
    list_universes,
    market_of,
)

st.set_page_config(page_title="Screener", page_icon="🔎", layout="wide")
st.title("🔎 Screener")

# --- Sidebar controls --------------------------------------------------------------

with st.sidebar:
    st.header("Filters")
    market = st.selectbox("Market", list_markets(), index=0)
    universe_name = st.selectbox("Universe", list_universes(market))
    strategy = st.radio("Strategy", ["scalping", "swing"], horizontal=True)

    custom_input = st.text_area(
        "Custom tickers (optional)",
        placeholder="BBCA.JK, BBRI.JK, AAPL, MSFT",
        help="Comma- or newline-separated. Overrides the universe if provided.",
    )

    st.divider()
    st.subheader("Risk settings")
    sl_mult = st.slider("SL multiplier (× ATR)", 0.5, 4.0, 1.5, 0.1)
    rr = st.slider("Risk : Reward (TP2)", 1.0, 5.0, 2.0, 0.5)

    st.divider()
    st.subheader("Position sizing (optional)")
    equity = st.number_input("Account equity", min_value=0.0, value=100_000_000.0, step=1_000_000.0)
    risk_pct = st.number_input("Risk per trade (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)


def _resolve_symbols() -> list[str]:
    if custom_input.strip():
        raw = custom_input.replace("\n", ",").split(",")
        return [normalize_symbol(s) for s in raw if s.strip()]
    return get_universe(market, universe_name)


symbols = _resolve_symbols()
st.caption(f"{len(symbols)} symbol(s) selected — strategy: **{strategy}**")

# --- Run scan ----------------------------------------------------------------------

run = st.button("Run scan", type="primary")
if run:
    if not symbols:
        st.warning("No symbols selected.")
        st.stop()

    progress = st.progress(0.0, text="Scanning…")
    results = []
    for i, _ in enumerate(symbols, start=1):
        progress.progress(i / len(symbols), text=f"Scanning {i}/{len(symbols)}")
    # Single-call scan (we already showed progress for UX).
    results = screen_universe(symbols, strategy)
    progress.empty()

    if not results:
        st.info("No candidates passed the filters. Try a different universe or relax the strategy.")
    else:
        rows = []
        for r in results:
            ccy = currency_of(r.symbol)
            rows.append({
                "Symbol": r.symbol,
                "Score": r.score,
                "Last": r.last,
                "Δ %": r.change_pct,
                "RSI": r.rsi,
                "ATR": r.atr,
                "ATR %": r.atr_pct,
                "Vol×": r.volume_ratio,
                "Reasons": ", ".join(r.reasons),
                "Currency": ccy,
            })
        df = pd.DataFrame(rows)
        st.success(f"{len(df)} candidate(s) found.")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.session_state["screener_results"] = [r.to_dict() for r in results]

# --- Drill-down: pick a candidate and see TP/SL plan -------------------------------

st.divider()
st.subheader("Trade plan (TP / SL)")

sel_symbol = st.text_input(
    "Symbol",
    value=(st.session_state.get("screener_results", [{}])[0].get("symbol", "") if st.session_state.get("screener_results") else ""),
    placeholder="e.g. BBCA.JK or AAPL",
).strip().upper()

if sel_symbol:
    side = st.radio("Side", ["long", "short"], horizontal=True, key="plan_side")
    df_d = fetch_history(sel_symbol, period="6mo", interval="1d")
    quote = fetch_quote(sel_symbol)
    if df_d.empty or not quote:
        st.error(f"No data for {sel_symbol}.")
    else:
        atr_v = float(atr(df_d["High"], df_d["Low"], df_d["Close"], 14).dropna().iloc[-1])
        entry = float(quote["price"])
        plan = calculate_trade_plan(entry=entry, atr_value=atr_v, side=side, sl_atr_mult=sl_mult, rr=rr)
        size = position_size(equity, risk_pct, plan.entry, plan.stop_loss)

        ccy = currency_of(sel_symbol)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Entry", f"{plan.entry:,.4f} {ccy}")
        col2.metric("Stop-Loss", f"{plan.stop_loss:,.4f}", f"-{plan.risk_per_share:,.4f}")
        col3.metric("ATR(14)", f"{plan.atr:,.4f}", f"{(plan.atr/entry*100):.2f}% of price")
        col4.metric("Risk : Reward", f"1 : {plan.risk_reward:.1f}")

        col5, col6, col7 = st.columns(3)
        col5.metric("TP1 (1R)", f"{plan.tp1:,.4f}")
        col6.metric(f"TP2 ({plan.risk_reward:.1f}R)", f"{plan.tp2:,.4f}")
        col7.metric(f"TP3 ({plan.risk_reward + 1:.1f}R)", f"{plan.tp3:,.4f}")

        st.markdown("**Position sizing**")
        col8, col9, col10 = st.columns(3)
        col8.metric("Risk amount", f"{size['risk_amount']:,.0f} {ccy}")
        col9.metric("Suggested qty", f"{size['qty']:,}")
        col10.metric("Estimated cost", f"{size['cost']:,.0f} {ccy}")

        # Save plan to session for the Positions page to pick up.
        st.session_state["last_plan"] = {
            "symbol": sel_symbol,
            "side": plan.side,
            "strategy": strategy,
            "entry": plan.entry,
            "qty": size["qty"],
            "stop_loss": plan.stop_loss,
            "take_profit": plan.tp2,
        }
        st.info(
            f"Open the **Positions** page and click *Save last plan* to log this trade "
            f"(TP={plan.tp2}, SL={plan.stop_loss}, qty={size['qty']}). "
            f"Symbol & side are pre-filled.",
            icon="ℹ️",
        )

st.caption(f"Currency hint based on symbol suffix. Detected market for sample symbol: {market_of(sel_symbol) if sel_symbol else '—'}")
