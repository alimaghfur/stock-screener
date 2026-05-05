# Stock Screener — IDX & US

A Streamlit app to screen Indonesian (IDX) and US stocks for **scalping** and **swing trading**, with automatic Take-Profit / Stop-Loss suggestions, top gainer/loser scanner, position tracking, and price alerts.

## Features

- **Screener** — scalping (intraday momentum) & swing (multi-day trend) filters with technical indicators (RSI, MACD, MA cross, ATR, VWAP, volume spike). IDX-only `BPJS` (Beli Pagi Jual Sore) and `BSJP` (Beli Sore Jual Pagi) pattern strategies.
- **TP / SL Suggestion** — ATR-based stop-loss with configurable risk:reward (default 1:2). Provides entry, SL, and three TP targets.
- **Top Movers** — top gainers and top losers per market (IDX: IDX30 / LQ45 / IDX80 / Kompas100; US: Dow 30 / Large Cap top ~100 / NASDAQ 100 / S&P 500).
- **News** — Yahoo Finance per-ticker articles (delayed) with thumbnails, plus an embedded TradingView Top Stories widget as a second source.
- **TradingView integration** — Advanced Chart and Technical Analysis gauge embedded in Screener drill-down for a "second opinion", plus a webhook receiver that captures TradingView alerts and surfaces them on the Alerts page.
- **Position Tracking** — log open positions (entry, qty, TP, SL), monitor live P/L, mark closed.
- **Alerts** — simple price-based alerts (price crosses above/below a level). Evaluated on each app refresh.

Data source is Yahoo Finance (delayed ~15 min via `yfinance`). The data layer is abstracted so a real-time provider can be plugged in later without touching the UI.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Markets & tickers

- **IDX**: tickers use the `.JK` suffix (e.g. `BBCA.JK`). Built-in universes:
  - **IDX30** (30) — most liquid IDX blue chips, refreshed quarterly by BEI.
  - **LQ45** (45) — top 45 most liquid + sizeable IDX names.
  - **IDX80** (~90) — extended IDX80 set.
  - **Kompas100** (~100) — broader 100-stock index, hand-curated snapshot from `id.wikipedia.org` plus the latest BEI Aug-Oct 2024 reshuffle. Refresh manually as compositions change.
- **US**: standard tickers (e.g. `AAPL`, dual-class with Yahoo dash convention `BRK-B`). Built-in universes:
  - **Dow 30** (30) — Dow Jones Industrial Average mega-caps.
  - **Large Cap (top ~100)** (106) — quick-scan curated subset for fast scans.
  - **NASDAQ 100** (101) — full NASDAQ-100 index (101 due to dual-class).
  - **S&P 500** (503) — full S&P 500 index (503 due to dual-class). Heaviest scan, slowest run.

Custom tickers can be entered directly in the Screener and News pages. Universe lists are hand-maintained snapshots in `core/universe.py` — refresh periodically from the source-of-truth tables (see comment at top of that file).

## Project layout

```
app.py                  # Streamlit entry, overview dashboard
pages/                  # Multipage Streamlit pages
  1_Screener.py
  2_Top_Movers.py
  3_Positions.py
  4_Alerts.py
  5_News.py
core/
  data.py               # yfinance fetcher (cached) + provider abstraction
  universe.py           # IDX & US ticker lists
  indicators.py         # RSI, MACD, MA, ATR, VWAP, volume spike
  screener.py           # scalping / swing / BPJS / BSJP scoring + filters
  risk.py               # ATR-based TP/SL calculator
  news.py               # Yahoo Finance news aggregation
  tradingview.py        # Symbol mapping + widget HTML + webhook payload parser
  db.py                 # SQLite store for positions, alerts, tv_alerts
tools/
  tradingview_webhook.py # FastAPI server receiving TradingView alert webhooks
tests/                  # pytest unit tests
```

## Testing

```bash
pytest -q
ruff check .
```

## TradingView integration

The Screener drill-down embeds the **TradingView Advanced Chart** and the
**Technical Analysis** gauge (Strong Buy / Buy / Neutral / Sell / Strong Sell)
as a second opinion next to the local technicals. The News page can swap
its source between Yahoo Finance and an embedded **TradingView Top Stories**
widget.

Symbol mapping is automatic (Yahoo `BBCA.JK` → TradingView `IDX:BBCA`,
`AAPL` → `NASDAQ:AAPL`, `BRK-B` → `NYSE:BRK.B`).

### Webhook receiver for TradingView alerts

A small FastAPI server in `tools/tradingview_webhook.py` accepts TradingView
alert webhooks and stores them in the `tv_alerts` SQLite table, where they are
rendered on the Alerts page.

Run locally:

```bash
uvicorn tools.tradingview_webhook:app --host 0.0.0.0 --port 8766
```

Expose it publicly so TradingView can reach it (ngrok example):

```bash
ngrok http 8766
# Copy the https://<random>.ngrok.io URL TradingView will hit.
```

Optionally protect the endpoint with a token:

```bash
export TRADINGVIEW_WEBHOOK_TOKEN=your-secret-here
```

When configured, callers must include `Authorization: Bearer your-secret-here`
in the request — TradingView supports this via the alert's HTTP headers field.

In TradingView's alert dialog, set the **Webhook URL** to
`https://<your-ngrok-host>/webhook/tradingview` and set the **Message** field to
either plain text (`{{ticker}} crossed {{plot_0_value}}`) or a JSON template:

```json
{"symbol": "{{ticker}}", "action": "above", "price": {{close}}}
```

Both formats are parsed.

## Notes & disclaimers

- All data is delayed; do not use this tool as the sole input for live trading decisions.
- TP/SL suggestions are mechanical (ATR + risk:reward) — confirm against your own analysis and risk tolerance.
- This is a research/learning tool. Not financial advice.
