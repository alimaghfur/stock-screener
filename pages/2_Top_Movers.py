"""Top Movers page — biggest gainers / losers per market & universe."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.screener import top_movers
from core.universe import currency_of, get_universe, list_markets, list_universes

st.set_page_config(page_title="Top Movers", page_icon="🏆", layout="wide")
st.title("🏆 Top Movers — Gainers & Losers")

with st.sidebar:
    st.header("Filters")
    market = st.selectbox("Market", list_markets(), index=0)
    universe_name = st.selectbox("Universe", list_universes(market))
    top_n = st.slider("How many", 5, 25, 10, 1)

symbols = get_universe(market, universe_name)
st.caption(f"Universe: **{universe_name}** ({len(symbols)} symbols)")

run = st.button("Refresh", type="primary")
if run or "movers_cache" not in st.session_state:
    with st.spinner("Fetching latest closes…"):
        gainers, losers = top_movers(symbols, top_n=top_n)
    st.session_state["movers_cache"] = (gainers, losers)

gainers, losers = st.session_state.get("movers_cache", ([], []))

if not gainers and not losers:
    st.info("No data yet. Click Refresh.")
else:
    ccy = currency_of(symbols[0]) if symbols else ""
    col_g, col_l = st.columns(2)

    def _fmt(rows):
        df = pd.DataFrame(rows)
        if df.empty:
            return df
        return df[["Symbol", "Last", "Prev Close", "Change", "Change %", "Volume"]]

    with col_g:
        st.subheader(f"📈 Top {len(gainers)} Gainers")
        df_g = _fmt(gainers)
        if df_g.empty:
            st.write("—")
        else:
            st.dataframe(
                df_g.style.format({
                    "Last": "{:,.2f}",
                    "Prev Close": "{:,.2f}",
                    "Change": "{:+,.2f}",
                    "Change %": "{:+.2f}%",
                    "Volume": "{:,.0f}",
                }),
                use_container_width=True,
                hide_index=True,
            )

    with col_l:
        st.subheader(f"📉 Top {len(losers)} Losers")
        df_l = _fmt(losers)
        if df_l.empty:
            st.write("—")
        else:
            st.dataframe(
                df_l.style.format({
                    "Last": "{:,.2f}",
                    "Prev Close": "{:,.2f}",
                    "Change": "{:+,.2f}",
                    "Change %": "{:+.2f}%",
                    "Volume": "{:,.0f}",
                }),
                use_container_width=True,
                hide_index=True,
            )

    st.caption(f"Prices in {ccy}. Change % computed from latest close vs previous close.")
