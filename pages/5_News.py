"""News page — latest headlines for IDX & US tickers from Yahoo Finance."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from core.data import normalize_symbol
from core.news import fetch_news_for_symbol, fetch_news_for_universe, humanize_age
from core.tradingview import WidgetConfig, top_stories_html
from core.universe import (
    currency_of,
    get_universe,
    list_markets,
    list_universes,
    market_of,
)

st.set_page_config(page_title="News", page_icon="📰", layout="wide")
st.title("📰 News")
st.caption(
    "Latest headlines per ticker from Yahoo Finance (delayed). "
    "Use this as a sanity check for technical signals — never as the only reason to enter."
)

# --- Sidebar controls --------------------------------------------------------------

with st.sidebar:
    st.header("Filters")
    source = st.radio(
        "Source",
        ["Yahoo Finance", "TradingView"],
        horizontal=True,
        help=(
            "Yahoo Finance: per-ticker article cards from yfinance (delayed). "
            "TradingView: embedded Top Stories widget (covers some IDX names "
            "Yahoo misses)."
        ),
    )
    market = st.selectbox("Market", list_markets(), index=0)
    universe_name = st.selectbox("Universe", list_universes(market))
    custom_input = st.text_area(
        "Custom tickers (optional)",
        placeholder="BBCA.JK, BBRI.JK, AAPL, MSFT",
        help="Comma- or newline-separated. Overrides the universe if provided.",
    )

    st.divider()
    if source == "Yahoo Finance":
        st.subheader("Display")
        per_symbol = st.slider("Articles per ticker", 1, 10, 3)
        max_total = st.slider("Max articles total", 5, 60, 25)
        show_thumbs = st.checkbox("Show thumbnails", value=True)
    else:
        st.subheader("TradingView widget")
        tv_focus = st.text_input(
            "Focus ticker (optional)",
            placeholder="BBCA.JK / AAPL",
            help=(
                "Leave empty to show TradingView's global top stories. Enter a "
                "ticker to filter the feed to that single name."
            ),
        )
        tv_height = st.slider("Widget height (px)", 400, 1000, 700, 50)
        per_symbol = 3
        max_total = 25
        show_thumbs = True


def _resolve_symbols() -> list[str]:
    if custom_input.strip():
        raw = custom_input.replace("\n", ",").split(",")
        return [normalize_symbol(s) for s in raw if s.strip()]
    return get_universe(market, universe_name)


symbols = _resolve_symbols()

# --- TradingView widget mode -------------------------------------------------------

if source == "TradingView":
    focus = tv_focus.strip().upper() if tv_focus else ""
    label = focus or "global feed"
    st.caption(
        f"Source: **TradingView Top Stories** — {label}. Widget is rendered "
        "directly by TradingView; news content is theirs, not Yahoo's."
    )
    cfg = WidgetConfig(theme="light", height=tv_height)
    components.html(
        top_stories_html(focus or None, cfg),
        height=tv_height + 20,
        scrolling=False,
    )
    st.stop()

# --- Header strip ------------------------------------------------------------------

col_info, col_action = st.columns([4, 1])
col_info.caption(
    f"{len(symbols)} ticker(s) · cached 10 min per ticker · "
    f"market: **{market}**"
)
if col_action.button("Refresh", help="Clear the news cache and re-fetch."):
    fetch_news_for_symbol.clear()
    st.rerun()

if not symbols:
    st.warning("No tickers selected. Pick a universe or enter custom tickers.")
    st.stop()

# --- Aggregate view ----------------------------------------------------------------

with st.spinner(f"Fetching news for {len(symbols)} ticker(s)…"):
    articles = fetch_news_for_universe(symbols, per_symbol=per_symbol, max_total=max_total)

if not articles:
    st.info(
        "No news articles found. Yahoo Finance coverage for IDX names can be sparse — "
        "try a different universe, add custom tickers, or pick well-covered names like "
        "TLKM.JK, BBRI.JK, or AAPL."
    )
    st.stop()

st.success(f"{len(articles)} article(s) — newest first.")

for art in articles:
    with st.container(border=True):
        if show_thumbs and art.thumbnail_url:
            cols = st.columns([1, 4])
            with cols[0]:
                st.image(art.thumbnail_url, use_container_width=True)
            body = cols[1]
        else:
            body = st.container()

        with body:
            if art.url:
                st.markdown(f"### [{art.title}]({art.url})")
            else:
                st.markdown(f"### {art.title}")

            tickers_str = ""
            if art.related_tickers:
                tickers_str = " · " + ", ".join(art.related_tickers[:5])
                if len(art.related_tickers) > 5:
                    tickers_str += f" +{len(art.related_tickers) - 5}"

            ccy = currency_of(art.related_tickers[0]) if art.related_tickers else ""
            mkt = market_of(art.related_tickers[0]) if art.related_tickers else ""
            mkt_chip = f" · {mkt}/{ccy}" if mkt else ""

            st.caption(
                f"**{art.publisher}** · {humanize_age(art.published_at)}"
                f"{mkt_chip}{tickers_str}"
            )
            if art.summary:
                st.write(art.summary)
