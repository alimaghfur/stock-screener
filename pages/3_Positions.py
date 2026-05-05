"""Positions page — recommended trade ideas with TP/SL, batched from a screener scan."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from core.data import fetch_history, fetch_quote
from core.indicators import atr as atr_indicator
from core.risk import calculate_trade_plan
from core.screener import screen_universe
from core.universe import currency_of, get_universe, list_markets, list_universes

st.set_page_config(page_title="Positions", page_icon="💼", layout="wide")
st.title("💼 Recommended Positions")
st.caption(
    "Auto-generated trade ideas. Pick a market & strategy, click Generate, and the app "
    "will scan the universe and produce a ready-to-act plan (entry / SL / TP1–TP3) for "
    "each candidate. Read-only — this page does not place orders."
)

# --- Sidebar controls --------------------------------------------------------------

with st.sidebar:
    st.header("Filters")
    market = st.selectbox("Market", list_markets(), index=0)
    universe_name = st.selectbox("Universe", list_universes(market))
    strategy = st.radio("Strategy", ["scalping", "swing"], horizontal=True)

    st.divider()
    st.subheader("Risk settings")
    sl_mult = st.slider("SL multiplier (× ATR)", 0.5, 4.0, 1.5, 0.1)
    rr = st.slider("Risk : Reward (TP2)", 1.0, 5.0, 2.0, 0.5)
    top_n = st.slider("Max recommendations", 3, 25, 10, 1)

symbols = get_universe(market, universe_name)
st.caption(f"Universe: **{universe_name}** ({len(symbols)} symbols) — strategy: **{strategy}**")

# --- Generate recommendations ------------------------------------------------------

generate = st.button("Generate recommendations", type="primary")
if generate:
    if not symbols:
        st.warning("No symbols selected.")
        st.stop()

    with st.spinner(f"Scanning {len(symbols)} symbols…"):
        results = screen_universe(symbols, strategy)

    if not results:
        st.info("No candidates passed the filters. Try a different universe or strategy.")
        st.session_state.pop("recommendations", None)
    else:
        rows = []
        for r in results[:top_n]:
            df_d = fetch_history(r.symbol, period="6mo", interval="1d")
            quote = fetch_quote(r.symbol)
            if df_d.empty or not quote:
                continue
            atr_series = atr_indicator(
                df_d["High"], df_d["Low"], df_d["Close"], 14
            ).dropna()
            if atr_series.empty:
                continue
            atr_v = float(atr_series.iloc[-1])
            entry = float(quote["price"])
            try:
                plan = calculate_trade_plan(
                    entry=entry,
                    atr_value=atr_v,
                    side=r.side,
                    sl_atr_mult=sl_mult,
                    rr=rr,
                )
            except ValueError:
                continue

            ccy = currency_of(r.symbol)
            rows.append({
                "Symbol": r.symbol,
                "Side": plan.side,
                "Strategy": r.strategy,
                "Score": r.score,
                "Entry": plan.entry,
                "Stop-Loss": plan.stop_loss,
                "TP1 (1R)": plan.tp1,
                f"TP2 ({plan.risk_reward:.1f}R)": plan.tp2,
                f"TP3 ({plan.risk_reward + 1:.1f}R)": plan.tp3,
                "ATR(14)": plan.atr,
                "Risk : Reward": f"1 : {plan.risk_reward:.1f}",
                "Reasons": ", ".join(r.reasons),
                "Currency": ccy,
            })

        st.session_state["recommendations"] = {
            "rows": rows,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "params": {
                "market": market,
                "universe": universe_name,
                "strategy": strategy,
                "sl_mult": sl_mult,
                "rr": rr,
                "top_n": top_n,
            },
        }

# --- Render last recommendations ---------------------------------------------------

cache = st.session_state.get("recommendations")
if cache and cache["rows"]:
    st.divider()
    params = cache["params"]
    st.subheader(f"Top {len(cache['rows'])} {params['strategy']} ideas — {params['universe']}")
    st.caption(
        f"Generated at {cache['generated_at']} UTC · "
        f"SL = {params['sl_mult']}× ATR · risk:reward = 1 : {params['rr']:.1f}"
    )

    df = pd.DataFrame(cache["rows"])
    price_cols = [c for c in df.columns if c in {"Entry", "Stop-Loss", "ATR(14)"} or c.startswith("TP")]
    fmt = {c: "{:,.4f}" for c in price_cols}
    fmt["Score"] = "{:.1f}"
    st.dataframe(
        df.style.format(fmt),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        "**How to read this table** — *Entry* uses the latest delayed quote. *Stop-Loss* "
        "is `entry ∓ SL_mult × ATR(14)`. *TP1/TP2/TP3* are `1R / rrR / (rr+1)R` from entry. "
        "Always sanity-check against support/resistance, news, and your own risk tolerance "
        "before acting."
    )
elif not generate:
    st.info("No recommendations yet. Set your filters in the sidebar and click *Generate recommendations*.")
