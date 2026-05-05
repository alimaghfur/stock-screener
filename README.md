# Stock Screener — IDX & US

A Streamlit app to screen Indonesian (IDX) and US stocks for **scalping** and **swing trading**, with automatic Take-Profit / Stop-Loss suggestions, top gainer/loser scanner, position tracking, and price alerts.

## Features

- **Screener** — scalping (intraday momentum) & swing (multi-day trend) filters with technical indicators (RSI, MACD, MA cross, ATR, VWAP, volume spike).
- **TP / SL Suggestion** — ATR-based stop-loss with configurable risk:reward (default 1:2). Provides entry, SL, and three TP targets.
- **Top Movers** — top gainers and top losers per market (IDX LQ45 / IDX30, US S&P 500 subset / NASDAQ 100 subset).
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

- **IDX**: tickers use the `.JK` suffix (e.g. `BBCA.JK`). Built-in universes: LQ45, IDX30, IDX80.
- **US**: standard tickers (e.g. `AAPL`). Built-in universes: S&P 500 top names, NASDAQ 100 top names.

Custom tickers can be entered directly in the Screener page.

## Project layout

```
app.py                  # Streamlit entry, overview dashboard
pages/                  # Multipage Streamlit pages
  1_Screener.py
  2_Top_Movers.py
  3_Positions.py
  4_Alerts.py
core/
  data.py               # yfinance fetcher (cached) + provider abstraction
  universe.py           # IDX & US ticker lists
  indicators.py         # RSI, MACD, MA, ATR, VWAP, volume spike
  screener.py           # scalping & swing scoring + filters
  risk.py               # ATR-based TP/SL calculator
  db.py                 # SQLite store for positions & alerts
tests/                  # pytest unit tests for indicators, risk, screener, db
```

## Testing

```bash
pytest -q
ruff check .
```

## Notes & disclaimers

- All data is delayed; do not use this tool as the sole input for live trading decisions.
- TP/SL suggestions are mechanical (ATR + risk:reward) — confirm against your own analysis and risk tolerance.
- This is a research/learning tool. Not financial advice.
