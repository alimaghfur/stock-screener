"""Stock Screener — IDX & US (Streamlit entry / overview page)."""

from __future__ import annotations

import streamlit as st

from core.db import init_db, list_alerts, list_positions

st.set_page_config(
    page_title="Stock Screener — IDX & US",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Make sure the SQLite schema exists before any page runs.
init_db()

st.title("📈 Stock Screener — IDX & US")
st.caption(
    "Scalping & swing screener with TP/SL suggestion, top movers, position tracking, "
    "and price alerts. Data: Yahoo Finance (delayed ~15 min)."
)

st.markdown(
    """
**Quick start**

1. **Screener** — pick a market & strategy (scalping / swing), pick a universe or enter custom tickers, and run.
2. **Top Movers** — see today's biggest gainers and losers.
3. **Positions** — log open trades with entry, TP, SL; track live P/L.
4. **Alerts** — set price alerts (above / below) per symbol.

Use the sidebar to navigate.
"""
)

col1, col2, col3 = st.columns(3)
open_positions = list_positions(status="open")
closed_positions = list_positions(status="closed")
active_alerts = list_alerts(status="active")

col1.metric("Open positions", len(open_positions))
col2.metric("Closed positions", len(closed_positions))
col3.metric("Active alerts", len(active_alerts))

st.divider()

st.subheader("How TP / SL is computed")
st.markdown(
    """
- **Stop-Loss (SL)** = entry − (`SL ATR multiplier` × ATR(14)) for long; opposite for short.
- **TP1** = +1R, **TP2** = +`risk:reward` × R, **TP3** = +(`rr` + 1) × R, where R is the per-share risk.
- Default: SL multiplier = 1.5 ATR, risk:reward = 2.0.

This is a mechanical rule of thumb — always sanity-check against support/resistance and your own risk tolerance.
"""
)

st.subheader("Disclaimer")
st.markdown(
    "Not financial advice. Data may be delayed. The screener is a research tool — "
    "always do your own due diligence."
)
