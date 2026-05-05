---
name: testing-stock-screener
description: End-to-end testing for the Streamlit stock-screener app (IDX + US). Use when verifying screener / positions / top-movers / alerts / news / TradingView integration changes.
---

# Testing the stock-screener app

Streamlit multi-page app + optional FastAPI webhook receiver. Yahoo Finance for prices/news, TradingView widgets for charts/news/TA gauge, SQLite for persistence.

## Setup

```bash
cd ~/repos/stock-screener
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt -r requirements-dev.txt
```

Start the Streamlit app (foreground; default port 8501 — use 8765 if you need to avoid conflicts):

```bash
streamlit run app.py --server.port 8765 --server.headless true
```

If you need the TradingView webhook receiver (PR #7), start it on a second port:

```bash
uvicorn tools.tradingview_webhook:app --host 0.0.0.0 --port 8766
```

The webhook server is a **separate process** from Streamlit. Don't expect Streamlit to spawn it.

## Streamlit hot-reload caveat (important)

New files dropped into `pages/` while the server is running do NOT show up in the sidebar nav until the Streamlit process restarts. If a test plan adds a new page (e.g. `pages/5_News.py`), restart Streamlit BEFORE testing — otherwise you'll get a confusing 404 / missing-link.

UI changes inside an existing page DO hot-reload normally.

## Test fixtures (well-known tickers)

| Symbol | Use for |
|---|---|
| `BBCA.JK` | IDX ticker · Yahoo news returns 0 articles → tests empty-state UI · TradingView maps to `IDX:BBCA` |
| `BBRI.JK` | IDX ticker · Yahoo returns ~1 article (low coverage) |
| `TLKM.JK` | IDX ticker · Yahoo returns ~8 articles (highest IDX coverage) |
| `GOTO.JK` | IDX ticker · used in IDX30 universe |
| `AAPL` | US ticker · NASDAQ branch · TradingView maps to `NASDAQ:AAPL` (NOT NYSE) · Yahoo returns 5+ articles |
| `MSFT` / `NVDA` / `GOOGL` | US ticker · NASDAQ branch |
| `BRK-B` | US ticker · NYSE branch · maps to `NYSE:BRK.B` (note Yahoo `-` → TV `.`) |

## Adversarial assertions that catch regressions

Use these unambiguous string / math checks instead of vague "looks right":

### 1. Trade plan math invariants

In the Screener drill-down or Positions table:

```
Entry − Stop-Loss ≈ sl_mult × ATR(14)    # tolerance < 1% of ATR
TP1 = Entry + 1R
TP2 = Entry + rr × R    # default rr = 2.0
TP3 = Entry + (rr+1) × R
where R = Entry − Stop-Loss
```

Sliding the SL multiplier (default 1.5) to 2.5 must visibly change `Entry−SL` in the table. Otherwise the slider is dead.

### 2. Strategy gating (IDX-only strategies)

BPJS and BSJP must appear in the Strategy radio ONLY when Market = IDX. Switch Market to US → both disappear. If they stay, `strategies_for_market()` is broken.

### 3. BPJS reasons text vs BSJP reasons text

Reasons column is the dispatcher proof:

- `BPJS` rows: `Avg O→C +X.XX% (20d), N/20 green days`
- `BSJP` rows: `Avg overnight gap +X.XX% (20d), N/20 gap-up days`

If both show the same text or one shows generic scalping reasons (`Above VWAP` / `RSI X momentum`), routing is broken.

### 4. BPJS threshold tip — "0 candidates" is real

Default BPJS thresholds (`_BPJS_MIN_EDGE = 0.003`, `_BPJS_MIN_GREEN = 0.60`) are tight. In low-volatility market regimes, IDX30 + IDX80 may legitimately return 0 candidates. The pipeline correctly shows the empty info message.

**To prove the BPJS branch actually wires up the table**, temporarily lower thresholds in `core/screener.py`, run the scan, then **`git checkout core/screener.py`** to revert before exiting test mode. Don't commit the relaxed thresholds.

### 5. TradingView symbol mapping

Caption below "TradingView chart" must literally read:
- `Mapped to IDX:BBCA on TradingView.` (for `BBCA.JK`)
- `Mapped to NASDAQ:AAPL on TradingView.` (for `AAPL`, NOT `NYSE:AAPL`)

Iframe `src` query string must include `symbol=IDX%3ABBCA` / `symbol=NASDAQ%3AAAPL`.

TA gauge must render a verdict label (one of: Strong Buy / Buy / Neutral / Sell / Strong Sell). Not blank, not stuck on "Loading…". Verdict should change between IDX and US tickers — this proves the widget responds to symbol prop changes.

### 6. News page Source toggle (PR #7)

Sidebar controls must SWAP when the radio changes:
- Yahoo: `Articles per ticker` slider, `Max articles total` slider, `Show thumbnails`
- TradingView: `Focus ticker (optional)` text input, `Widget height (px)` slider

If the sidebar doesn't change when toggling, the radio is broken.

### 7. Webhook receiver inverse mapping (PR #7)

```bash
curl -X POST http://localhost:8766/webhook/tradingview \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"IDX:BBCA","action":"above","price":9000}'
```

Response JSON must show `"symbol":"BBCA.JK"` (Yahoo style, NOT `IDX:BBCA`). The Alerts page table must persist the same Yahoo-style symbol — this is unambiguous proof of the inverse mapper.

Plain-text alerts also work:
```bash
curl -X POST http://localhost:8766/webhook/tradingview \
  -H 'Content-Type: text/plain' \
  --data "AAPL crossed above 175.50"
```
Response should parse to `{"symbol":"AAPL","condition":"above","value":175.5}`.

## Streamlit form gotcha

`st.form` + `st.number_input`: pressing Enter while typing in `number_input` submits the form before the value commits. Workaround: type → click another field → click Save (don't use Enter).

This is a known Streamlit behavior, not a bug in our code. If you see duplicate alerts after form submit, you probably hit this.

## Top Movers caching

The currency footer (`Prices in IDR` vs `USD`) reads from the universe selector. If you switch market without clicking Refresh, you may briefly see `USD` over cached IDX data. Self-corrects after Refresh.

## Lint + tests

```bash
ruff check .
pytest -q                   # must be all green before opening PR
```

Number of unit tests as of PR #7: **89** (across `tests/test_data.py`, `test_db.py`, `test_indicators.py`, `test_news.py`, `test_risk.py`, `test_screener.py`, `test_tradingview.py`).

## Devin Secrets Needed

None for default flows. The TradingView webhook can optionally require a token via `TV_WEBHOOK_TOKEN` env var; for testing we leave it unset.

## Reusable test plans

- `test-plan.md` — initial 4-flow test (Screener / Top Movers / Positions form / Alerts) — superseded by PR #3 redesign
- `test-plan-v2.md` — Positions read-only recommendations (post-PR #3)
- `test-plan-bpjs-bsjp.md` + `test-plan-bpjs-bsjp-v2.md` — BPJS/BSJP strategies (post-PR #4)
- `test-plan-news.md` — News page + Screener news drill-down (post-PR #5)
- `test-plan-tradingview.md` — TradingView chart/gauge/news/webhook (post-PR #7)

These live in the repo root and should be reused or extended for future tests.
